from playwright.async_api import Page, BrowserContext
import asyncio
import os


class Fgts:
    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        await page.goto(
            "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"
        )
        await page.fill("//*[@id='mainForm:txtInscricao1']", cnpj)
        await asyncio.sleep(4)
        await page.click("//*[@id='mainForm:btnConsultar']")

        text = await page.locator("//span[@class='feedback-text']").inner_text()
        print(text.strip().lower(), flush=True)
        if (
            text.strip().lower()
            == "a empresa abaixo identificada está regular perante o fgts:"
        ):
            await page.click("//*[@id='mainForm:j_id51']")
            await page.click("//*[@id='mainForm:btnVisualizar']")
            await asyncio.sleep(0.5)
            filename = os.urandom(6).hex()
            await page.pdf(path=f"{filename}.pdf", format="A4")
            return {"status": "found", "filename": filename, "message": "success"}
        else:
            return {"status": 404, "message": "cant_generate"}
