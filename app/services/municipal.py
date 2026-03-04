from playwright.async_api import Page, BrowserContext


class Municipal:
    @staticmethod
    async def sc_florianopolis(page: Page, context: BrowserContext, cnpj: str):
        await page.goto("https://e-gov.betha.com.br/cdweb/")
        await page.select_option("//select[@id='mainForm:estados']", ["22"])
        await page.select_option("//select[@id='mainForm:municipios']", ["22"])
        await page.click("//*[@id='mainForm:selecionar']")
        await page.click("//div[contains(@class, 'cndContr')]")
        await page.click("//a[contains(@class, 'cnpj')]")
        await page.fill("//*[@id='mainForm:cnpj']", cnpj)
        await page.click("//*[@id='mainForm:btCnpj']")
        await page.click("//*[@id='mainForm:t-contribuinte']/tbody/tr/td[3]/img")
        iframe = page.frame_locator("//iframe[@class='fancybox-iframe']")
        async with page.expect_download() as download_info:
            await iframe.locator("//*[@id='download']").click()
        download = await download_info.value
        await download.save_as("arquivo_municipal.pdf")
