import asyncio
import base64
import functools
from urllib.parse import urlparse, parse_qs
from playwright.async_api import Page
from twocaptcha import TwoCaptcha
from app.config import logger, state


class CaptchaSolver:
    @staticmethod
    async def _run(func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, functools.partial(func, *args, **kwargs)
        )

    @staticmethod
    def _extract_sitekey(src: str) -> str:
        params = parse_qs(urlparse(src).query)
        keys = params.get("k") or params.get("sitekey")
        if not keys:
            logger.error("[CaptchaSolver] sitekey not found in iframe src")
            raise ValueError(f"sitekey not found in iframe src: {src!r}")
        return keys[0]



    @staticmethod
    async def solve(
        api_key: str, page: Page, img_xpath: str = None, input_xpath: str = None
    ) -> str:
        mode = "image" if img_xpath else "recaptcha"
        logger.info(f"[CaptchaSolver] Starting solve mode={mode} url={page.url}")
        solver = TwoCaptcha(api_key)

        if not img_xpath:
            iframe = page.locator("//iframe[@title='reCAPTCHA']").first
            src = await iframe.get_attribute("src")

            if not src:
                logger.error("[CaptchaSolver] reCAPTCHA iframe src not found")
                raise RuntimeError("[CaptchaSolver] reCAPTCHA iframe src not found")

            sitekey = CaptchaSolver._extract_sitekey(src)

            logger.debug(
                f"[CaptchaSolver] Sending reCAPTCHA to provider sitekey={sitekey[:8]}..."
            )

            logger.debug("tentando achar item")
            token = (
                await CaptchaSolver._run(
                    solver.recaptcha, sitekey=sitekey, url=page.url
                )
            )["code"]

            logger.debug(
                f"[CaptchaSolver] Token received successfully len={len(token)}"
            )

            await page.locator("//textarea[@id='g-recaptcha-response']").evaluate(
                "(el) => el.style.display = 'block'"
            )
            await page.locator("//textarea[@id='g-recaptcha-response']").fill(token)
            await page.locator("//textarea[@id='g-recaptcha-response']").evaluate(
                "(el) => el.style.display = 'none'"
            )

            logger.info("[CaptchaSolver] reCAPTCHA solved and token injected")
            return token

        else:
            logger.debug(f"[CaptchaSolver] Capturing captcha image xpath={img_xpath}")
            img_b64 = base64.b64encode(
                await page.locator(img_xpath).screenshot()
            ).decode("utf-8")
            result = await CaptchaSolver._run(solver.normal, img_b64, caseSensitive=1)
            code = result["code"]
            await page.locator(input_xpath).fill(code)
            logger.info("[CaptchaSolver] Image captcha solved and input filled")
            return code
