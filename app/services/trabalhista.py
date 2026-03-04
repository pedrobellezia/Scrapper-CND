from playwright.async_api import Page, BrowserContext
import asyncio
import base64

from app.utils import CaptchaSolver


class Trabalhista:
    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        await page.goto("https://cndt-certidao.tst.jus.br/inicio.faces")
        await page.click("//*[@id='corpo']/div/div[2]/input[1]")
        await page.fill("//*[@id='gerarCertidaoForm:cpfCnpj']", cnpj)
        await asyncio.sleep(4)
        data = await page.locator('//*[@id="idImgBase64"]').screenshot()
        b64 = base64.b64encode(data).decode("utf-8")

        await CaptchaSolver.solve_captcha(
            page=page,
            img64=b64,
            version="normal",
            input_xpath="//*[@id='idCampoResposta']",
        )
        async with page.expect_download() as download_info:
            await page.click("//*[@id='gerarCertidaoForm:btnEmitirCertidao']")
        download = await download_info.value
        await download.save_as("arquivo.pdf")
