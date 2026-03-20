from datetime import datetime
from playwright.async_api import (
    Page,
    BrowserContext,
    TimeoutError as PlaywrightTimeout,
    Download,
)
from app.exceptions import ScrapError, WrongParams
from app.config import logger, CAPTCHA_API_KEY
from app.utils.captcha_solver import CaptchaSolver
from app.services.error_utils import raise_timeout, raise_unexpected
from pathlib import Path
import asyncio


class Estadual:
    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str, uf: str):
        logger.info(f"Starting Estadual scrape for CNPJ: {cnpj}, UF: {uf}")

        uf_key = uf.lower()
        if not uf_key.isalpha() or len(uf_key) != 2:
            raise WrongParams(f"UF '{uf}' invalida")

        method = getattr(Estadual, uf_key, None)
        if not callable(method) or uf_key.startswith("_"):
            raise WrongParams(f"UF '{uf}' nao suportada")

        return await method(page=page, context=context, cnpj=cnpj)

    @staticmethod
    async def sp(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Estadual SP scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://www10.fazenda.sp.gov.br/CertidaoNegativaDeb/Pages/EmissaoCertidaoNegativa.aspx",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await page.locator("//*[@id='MainContent_cnpjradio']").click()
            await page.locator("//*[@id='MainContent_txtDocumento']").fill(cnpj)

            await CaptchaSolver.solve(api_key=CAPTCHA_API_KEY, page=page)

            await page.locator("//*[@id='MainContent_btnPesquisar']").click()
            await asyncio.sleep(5)

            if await page.locator("//*[@class='bg-danger']").is_visible():
                raise ScrapError(
                    f"Nao foi possivel obter a certidao para o CNPJ {cnpj} em SP"
                )

            async with page.expect_download(timeout=30_000) as dl:
                await page.locator("//*[@id='MainContent_btnImpressao']").click()
            download = await dl.value
            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF Estadual SP para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Estadual SP scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Estadual SP", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Estadual SP", cnpj, page, e)

    @staticmethod
    async def sc(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Estadual SC scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://sat.sef.sc.gov.br/tax.NET/Sat.CtaCte.Web/SolicitacaoCnd.aspx"
            )

            await page.locator(
                "//*[@id='Body_Main_Main_sepBusca_idnCnd_MaskedField']"
            ).fill(cnpj)

            await CaptchaSolver.solve(api_key=CAPTCHA_API_KEY, page=page)

            await page.locator(
                "//a[.//span[contains(normalize-space(), 'Buscar')]]"
            ).click()

            rows = page.locator(
                "//table[@id='Body_Main_Main_ctnResultado_grpCnd_gridView']"
            ).locator("tbody tr")

            await asyncio.sleep(1)

            count = await rows.count()
            logger.info(f"Found {count} CND rows for CNPJ {cnpj}")

            for i in range(count - 1):
                logger.info(f"Checking CND row {i + 1}/{count} for CNPJ {cnpj}")
                row = rows.nth(i)
                cnd_date = row.locator("td").nth(3).locator("span")

                cls = await cnd_date.get_attribute("class")
                valid = cls and "valido" in cls

                date_text = await cnd_date.inner_text()
                expired = (
                    datetime.strptime(date_text, "%d/%m/%Y").date()
                    < datetime.today().date()
                )

                if valid and not expired:
                    download_button = row.locator("td").nth(4).locator("a")

                    async with page.expect_download(timeout=30000) as download_info:
                        await download_button.click()

                    download = await download_info.value

                    download_path = await download.path()
                    if not download_path:
                        raise ScrapError(f"Falha ao obter PDF Estadual SC para {cnpj}")
                    pdf_bytes = Path(download_path).read_bytes()

                    return pdf_bytes

            try:
                download_task = asyncio.create_task(page.wait_for_event("download"))
                popup_task = asyncio.create_task(page.wait_for_event("popup"))

                await page.click('//*[@id="Body_Main_Main_ctnResultado_btnGerarCnd"]')

                done, _ = await asyncio.wait(
                    [download_task, popup_task], return_when=asyncio.FIRST_COMPLETED
                )

                if download_task in done:
                    download: Download = await download_task
                    popup_task.cancel()

                else:
                    popup: Page = await popup_task
                    download_task.cancel()
                    await popup.emulate_media(media="print")
                    return await popup.pdf()

            except PlaywrightTimeout:
                link = page.locator('//ul[@class="sat-vs-success"]/li[3]/a')

                async with page.expect_download(timeout=30_000) as dl:
                    await link.click()

                download = await dl.value

            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF Estadual SC para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Estadual SC scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Estadual SC", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Estadual SC", cnpj, page, e)
