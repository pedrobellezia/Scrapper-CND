import asyncio
from playwright.async_api import Page
from twocaptcha import TwoCaptcha
import concurrent.futures
from os import environ


class CaptchaSolver:
    @classmethod
    async def solve_captcha(
        cls, page: Page, version: str, img64=None, input_xpath=None
    ):
        loop = asyncio.get_running_loop()
        solver = TwoCaptcha(environ.get("CAPTCHA_API_KEY"))
        with concurrent.futures.ThreadPoolExecutor() as pool:
            if version == "recaptcha":
                await cls.__solve_recaptcha(
                    page=page, loop=loop, solver=solver, pool=pool
                )
            elif version == "normal":
                await cls.__solve_normal(
                    img64=img64,
                    input_xpath=input_xpath,
                    page=page,
                    loop=loop,
                    solver=solver,
                    pool=pool,
                )
            else:
                raise ValueError("Unsupported CAPTCHA version")

    @staticmethod
    async def __solve_recaptcha(page: Page, loop, solver, pool):
        src = await page.locator("//iframe[@title = 'reCAPTCHA']").first.get_attribute(
            "src"
        )
        sitekey = src.split("k=")[1].split("&")[0]
        url = page.url
        result = await loop.run_in_executor(
            pool, lambda: solver.recaptcha(sitekey=sitekey, url=url)
        )
        token = result["code"]
        await page.locator("//textarea[@id='g-recaptcha-response']").evaluate(
            "(el) => el.style.display = 'block'"
        )
        await page.locator("//textarea[@id='g-recaptcha-response']").fill(token)
        await page.locator("//textarea[@id='g-recaptcha-response']").evaluate(
            "(el) => el.style.display = 'none'"
        )

    @staticmethod
    async def __solve_normal(
        img64: str, input_xpath: str, page: Page, loop, solver, pool
    ):
        result = await loop.run_in_executor(
            pool, lambda: solver.normal(img64, caseSensitive=1)["code"]
        )
        await page.locator(input_xpath).fill(result)
