from playwright.async_api import (
    Page,
    BrowserContext,
    TimeoutError as PlaywrightTimeout,
    Download,
)
import httpx
from app.exceptions import ScrapError, WrongParams
from app.config import logger, CAPTCHA_API_KEY
from app.utils.captcha_solver import CaptchaSolver
from app.services.error_utils import raise_timeout, raise_unexpected
from pathlib import Path
import asyncio
import random


class Municipal:
    @staticmethod
    async def execute_scrap(
        page: Page, context: BrowserContext, cnpj: str, uf: str, municipio: str
    ):
        logger.info(f"Starting Municipal scrape for CNPJ: {cnpj}, {municipio}/{uf}")

        uf_key = uf.lower()
        municipio_key = municipio.lower().replace(" ", "_")

        if not uf_key.isalpha() or len(uf_key) != 2:
            raise WrongParams(f"UF '{uf}' inválida")

        if not municipio_key.replace("_", "").isalpha():
            raise WrongParams(f"Município '{municipio}' inválido")

        method_name = f"{uf_key}_{municipio_key}"
        if method_name.startswith("_"):
            raise WrongParams(f"Município '{municipio}/{uf}' inválido")

        method = getattr(Municipal, method_name, None)
        if not callable(method):
            raise WrongParams(f"Município '{municipio}/{uf}' não suportado")

        return await method(page, context, cnpj)

    @staticmethod
    async def solve_betha(
        page: Page,
        context: BrowserContext,
        cnpj: str,
        municipio_id: str,
        estado_id: str,
    ) -> Download:
        await page.goto(
            "https://e-gov.betha.com.br/cdweb/",
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        await page.locator("//select[@id='mainForm:estados']").select_option(estado_id)
        await page.locator("//select[@id='mainForm:municipios']").select_option(
            municipio_id
        )
        await page.locator("//*[@id='mainForm:selecionar']").click()
        await page.locator("//div[contains(@class, 'cndContr')]").click()
        await page.locator("//a[contains(@class, 'cnpj')]").click()
        await asyncio.sleep(1)
        await page.locator("//*[@id='mainForm:cnpj']").fill(cnpj)
        await asyncio.sleep(1)
        await page.locator("//*[@id='mainForm:btCnpj']").click()

        t = page.locator('//strong[@class="fieldError"]')

        if await t.count() > 0:
            await asyncio.sleep(1)
            await page.locator("//*[@id='mainForm:cnpj']").fill(cnpj)
            await asyncio.sleep(1)
            await page.locator("//*[@id='mainForm:btCnpj']").click()

        await page.locator(
            "//*[@id='mainForm:t-contribuinte']/tbody/tr/td[3]/img"
        ).click()

        async with page.expect_download(timeout=30_000) as dl:
            await (
                page.frame_locator("//iframe[@class='fancybox-iframe']")
                .locator("//*[@id='download']")
                .click()
            )
        return await dl.value

    @staticmethod
    async def _download_to_buffer(download: Download, cnpj: str, source: str) -> bytes:
        download_path = await download.path()
        if not download_path:
            raise ScrapError(f"Falha ao obter PDF {source} para {cnpj}")
        return Path(download_path).read_bytes()

    @staticmethod
    async def sc_blumenau(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Municipal SC/Blumenau scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://www.blumenau.sc.gov.br/cidadao/pages/siatu/cnd/EmissaoCND.aspx",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await page.locator(
                "//*[@name='ctl00$ContentBody$cbkEmissaoCND$txtCpfCnpj']"
            ).fill(cnpj)

            await CaptchaSolver.solve(
                api_key=CAPTCHA_API_KEY,
                page=page,
                img_xpath="//*[@id='ctl00_ContentBody_cbkEmissaoCND_ImageCaptcha']",
                input_xpath="//*[@id='ctl00_ContentBody_cbkEmissaoCND_tbCaptcha_I']",
            )

            await page.locator(
                "//*[@id='ctl00_ContentBody_cbkEmissaoCND_btPesquisar']"
            ).click()

            await asyncio.sleep(5)

            async with page.expect_download(timeout=30_000) as dl:
                await page.locator("//*[@id='ctl00_ContentBody_btnImprimir']").click()
            download = await dl.value
            pdf_buffer = await Municipal._download_to_buffer(
                download, cnpj, "Municipal SC/Blumenau"
            )

            logger.info(f"Municipal SC/Blumenau scrape completed for CNPJ: {cnpj}")
            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Blumenau", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Blumenau", cnpj, page, e)

    @classmethod
    async def sc_florianopolis(cls, page: Page, context: BrowserContext, cnpj: str):
        try:
            download_info = await cls.solve_betha(
                page, context, cnpj, municipio_id="94", estado_id="22"
            )
            pdf_buffer = await cls._download_to_buffer(
                download_info, cnpj, "Municipal SC/Florianopolis"
            )

            logger.info(f"Municipal SC/Florianopolis scrape completed for CNPJ: {cnpj}")
            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Florianopolis", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Florianopolis", cnpj, page, e)

    @classmethod
    async def sc_lages(cls, page: Page, context: BrowserContext, cnpj: str):
        try:
            download_info = await cls.solve_betha(
                page, context, cnpj, municipio_id="35", estado_id="22"
            )
            pdf_buffer = await cls._download_to_buffer(
                download_info, cnpj, "Municipal SC/Lages"
            )

            logger.info(f"Municipal SC/Lages scrape completed for CNPJ: {cnpj}")
            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Lages", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Lages", cnpj, page, e)

    @classmethod
    async def sc_braco_do_norte(cls, page: Page, context: BrowserContext, cnpj: str):
        try:
            download_info = await cls.solve_betha(
                page, context, cnpj, municipio_id="91", estado_id="22"
            )
            pdf_buffer = await cls._download_to_buffer(
                download_info, cnpj, "Municipal SC/Braco do Norte"
            )

            logger.info(
                f"Municipal SC/Braco do Norte scrape completed for CNPJ: {cnpj}"
            )
            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Braco do Norte", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Braco do Norte", cnpj, page, e)

    @classmethod
    async def sc_criciuma(cls, page: Page, context: BrowserContext, cnpj: str):
        try:
            download_info = await cls.solve_betha(
                page, context, cnpj, municipio_id="29", estado_id="22"
            )
            pdf_buffer = await cls._download_to_buffer(
                download_info, cnpj, "Municipal SC/Criciuma"
            )

            logger.info(f"Municipal SC/Criciuma scrape completed for CNPJ: {cnpj}")
            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Criciuma", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Criciuma", cnpj, page, e)

    @staticmethod
    async def sc_itapema(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Municipal SC/Itapema scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://itapema-sc.prefeituramoderna.com.br/meuiptu/index.php",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await asyncio.sleep(0.5)
            await page.locator("//a[@id='cnd']").click()
            await page.locator("//input[@name='nrcpfcnpj']").fill(cnpj)
            await page.locator("//input[@name='nmrequerente']").fill("segredo")
            await page.locator("//input[@name='nrdocumento']").fill("52998224725")

            async with page.expect_popup() as popup_info:
                await page.locator("//input[@value='Emitir a Certidão']").click()
            popup = await popup_info.value

            await popup.emulate_media(media="print")
            pdf_buffer = await popup.pdf(format="A4")

            logger.info(f"Municipal SC/Itapema scrape completed for CNPJ: {cnpj}")

            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Itapema", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Itapema", cnpj, page, e)

    @staticmethod
    async def sc_balneario_camboriu(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Municipal SC/Camboriu scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://cidadao.bc.sc.gov.br/cidadao/balneario_camboriu/portal/servicos/certidoes/emissao?params=MTU%3D",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.locator(
                "//select[@formcontrolname='idFinalidade']"
            ).select_option(value="1: 5")

            await page.locator("//input[@formcontrolname='cpfCnpj']").fill(cnpj)

            await page.locator("//cidadao-button[@type='submit']").click()

            async with page.expect_download(timeout=30_000) as dl:
                await page.locator("//cidadao-button[@icon='fa fa-download']").click()
            download = await dl.value
            pdf_buffer = await Municipal._download_to_buffer(
                download, cnpj, "Municipal SC/Camboriu"
            )

            logger.info(f"Municipal SC/Camboriu scrape completed for CNPJ: {cnpj}")

            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Camboriu", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Camboriu", cnpj, page, e)

    @staticmethod
    async def sc_joinville(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Municipal SC/Joinville scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://tmiweb.joinville.sc.gov.br/sefaz/jsp/cnd/index.jsp"
            )

            await page.locator("//select[@id='finalidade']").select_option(value="6")

            await page.locator("//input[@name='cnpj']").fill(cnpj)

            await page.locator("//input[@value='Pesquisar']").click()

            await page.locator("//select[@id='ctp_codigo']").select_option(value="8")

            await page.locator("//input[contains(@value, 'Gerar cert')]").click()

            await asyncio.sleep(1)
            url = page.url

            reponse = httpx.get(url)
            if reponse.status_code != 200:
                raise ScrapError(
                    f"Falha ao obter PDF Municipal SC/Joinville para {cnpj}, status code: {reponse.status_code}"
                )

            pdf_buffer = reponse.content

            logger.info(f"Municipal SC/Joinville scrape completed for CNPJ: {cnpj}")

            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Joinville", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Joinville", cnpj, page, e)

    @staticmethod
    async def sp_sao_paulo(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Municipal SP/Sao Paulo scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://duc.prefeitura.sp.gov.br/certidoes/forms_anonimo/frmConsultaEmissaoCertificado.aspx"
            )
            await asyncio.sleep(random.uniform(1, 2))

            await page.locator(
                '//*[@id="ctl00_ConteudoPrincipal_ddlTipoCertidao"]'
            ).select_option(value="1")

            await asyncio.sleep(random.uniform(1, 2))

            await page.locator('//*[@id="ctl00_ConteudoPrincipal_txtCNPJ"]').fill(cnpj)

            await asyncio.sleep(random.uniform(1, 2))
            imgpath = '//*[@id="ctl00_ConteudoPrincipal_imgCaptcha"]'
            input_path = '//*[@id="ctl00_ConteudoPrincipal_txtValorCaptcha"]'
            await CaptchaSolver.solve(
                api_key=CAPTCHA_API_KEY,
                page=page,
                img_xpath=imgpath,
                input_xpath=input_path,
            )

            await asyncio.sleep(random.uniform(1, 2))

            await page.click('//*[@id="ctl00_ConteudoPrincipal_btnEmitir"]')

            await CaptchaSolver.solve(
                api_key=CAPTCHA_API_KEY,
                page=page,
                img_xpath="xpath=/html/body/img[1]",
                input_xpath='//*[@id="ans"]',
            )

            async with page.expect_download(timeout=30_000) as dl:
                await page.click('//*[@id="jar"]')

            download = await dl.value
            pdf_buffer = await Municipal._download_to_buffer(
                download, cnpj, "Municipal SP/Sao Paulo"
            )

            logger.info(f"Municipal SP/Sao Paulo scrape completed for CNPJ: {cnpj}")

            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SP/Sao Paulo", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SP/Sao Paulo", cnpj, page, e)

    @staticmethod
    async def sc_icara(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Municipal SC/Icara scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://icara-sc.prefeituramoderna.com.br/meuiptu/index.php",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await asyncio.sleep(1)
            await page.locator("//a[@id='cnd']").click()
            await page.locator("//input[@name='nrcpfcnpj']").fill(cnpj)
            await page.locator("//input[@name='nmrequerente']").fill("segredo")
            await page.locator("//input[@name='nrdocumento']").fill("52998224725")

            async with page.expect_popup() as popup_info:
                await page.locator("//input[@value='Emitir a Certidão']").click()
            popup = await popup_info.value

            await popup.emulate_media(media="print")
            pdf_buffer = await popup.pdf(format="A4")

            logger.info(f"Municipal SC/Icara scrape completed for CNPJ: {cnpj}")

            return pdf_buffer

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("Municipal SC/Icara", cnpj, page, e)
        except Exception as e:
            raise_unexpected("Municipal SC/Icara", cnpj, page, e)
