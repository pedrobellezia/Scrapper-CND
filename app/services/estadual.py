from playwright.async_api import Page, BrowserContext
from datetime import datetime, timedelta
from app.utils import CaptchaSolver
import asyncio


class Estadual:
    @staticmethod
    async def sc(page: Page, context: BrowserContext, cnpj: str):
        await page.goto(
            "https://sat.sef.sc.gov.br/tax.NET/Sat.CtaCte.Web/SolicitacaoCnd.aspx"
        )
        await page.fill("//*[@id='Body_Main_Main_sepBusca_idnCnd_MaskedField']", cnpj)

        await CaptchaSolver.solve_captcha(
            page=page,
            version="recaptcha",
        )
        await page.click("//a[.//span[contains(normalize-space(), 'Buscar')]]")
        try:
            validade = page.locator(
                '//table[@id="Body_Main_Main_ctnResultado_grpCnd_gridView"]/tbody/tr/td[4]/span[contains(@class, "valido")]'
            ).first
            await validade.wait_for(timeout=10000)
            text = await validade.inner_text()
            date_from_text = datetime.strptime(text, "%d/%m/%Y").date()
            if date_from_text <= datetime.today().date() + timedelta(days=3):
                raise TimeoutError

            async with page.expect_download() as download_info:
                await page.locator(
                    '//*[@id="Body_Main_Main_ctnResultado_grpCnd_gridView_cmd0_0"]'
                ).click()
            download = await download_info.value
            await download.save_as("arquivo_municipal.pdf")

        except TimeoutError:
            popup_task = asyncio.create_task(
                page.wait_for_event("popup", timeout=10000)
            )
            download_task = asyncio.create_task(
                page.wait_for_event("download", timeout=10000)
            )
            await page.click(
                "//a[.//span[contains(normalize-space(), 'Solicitar nova CND')]]"
            )

            try:
                download = await download_task
                await download.save_as("arquivo_municipal.pdf")
                return
            except TimeoutError:
                pass

            try:
                popup = await popup_task
                await popup.wait_for_load_state("networkidle")
                await page.pdf(path="arquivo_municipal.pdf", format="A4")
            except TimeoutError:
                pass

    @staticmethod
    async def sp(page: Page, context: BrowserContext, cnpj: str):
        await page.goto(
            "https://www10.fazenda.sp.gov.br/CertidaoNegativaDeb/Pages/EmissaoCertidaoNegativa.aspx"
        )

        await page.click("//*[@id='MainContent_cnpjradio']")
        await page.fill("//*[@id='MainContent_txtDocumento']", cnpj)
        await CaptchaSolver.solve_captcha(
            page=page,
            version="recaptcha",
        )
        await page.click("//*[@id='MainContent_btnPesquisar']")
        async with page.expect_download() as download_info:
            await page.click("//*[@id='MainContent_btnImpressao']")
        download = await download_info.value
        await download.save_as("arquivo_estadual.pdf")
