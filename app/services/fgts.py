from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout
from app.exceptions import ScrapError, WrongParams
from app.config import logger
from app.services.error_utils import raise_timeout, raise_unexpected
import asyncio


class Fgts:
    URL = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"

    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting FGTS scrape for CNPJ: {cnpj}")

            await page.goto(Fgts.URL, wait_until="domcontentloaded", timeout=30_000)

            cnpj_field = page.locator("//*[@id='mainForm:txtInscricao1']")
            await cnpj_field.wait_for(state="visible", timeout=10_000)
            await cnpj_field.fill(cnpj)

            await page.locator("//*[@id='mainForm:btnConsultar']").click()
            await page.wait_for_load_state("networkidle", timeout=20_000)

            result_row = page.locator("//*[@id='mainForm:j_id51']")
            try:
                await result_row.wait_for(state="visible", timeout=10_000)
            except PlaywrightTimeout:
                raise WrongParams(f"CNPJ {cnpj} nao encontrado na consulta FGTS")
            await result_row.click()
            await page.wait_for_load_state("networkidle", timeout=20_000)

            visualizar_btn = page.locator("//*[@id='mainForm:btnVisualizar']")
            try:
                await visualizar_btn.wait_for(state="visible", timeout=10_000)
            except PlaywrightTimeout:
                raise ScrapError(f"Botao Visualizar nao encontrado para CNPJ {cnpj}")
            await visualizar_btn.click()
            await asyncio.sleep(1)
            await page.wait_for_load_state("networkidle", timeout=20_000)


            try:
                pdf_bytes = await page.pdf()
            except Exception as pdf_err:
                raise ScrapError(
                    f"Falha ao gerar PDF para CNPJ {cnpj}. Detalhe: {type(pdf_err).__name__}: {pdf_err}"
                ) from pdf_err

            logger.info(f"FGTS scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except (ScrapError, WrongParams):
            raise
        except PlaywrightTimeout as e:
            raise_timeout("FGTS", cnpj, page, e)
        except Exception as e:
            raise_unexpected("FGTS", cnpj, page, e)
