from typing import Optional
from playwright.async_api import Browser
import asyncio
from functools import lru_cache

# Global state
browser: Optional[Browser] = None
semaphore = asyncio.Semaphore(3)


async def get_tools():
    if browser is None:
        raise RuntimeError(
            "Browser não inicializado. Verifique o lifespan da aplicação."
        )

    async with semaphore:
        context = None
        page = None
        try:
            context = await browser.new_context()

            page = await context.new_page()
            yield page, context
        except Exception:
            raise
        finally:
            await page.close() if page else None
            await context.close() if context else None


@lru_cache
def get_browser() -> Browser:
    global browser
    if browser is None:
        raise RuntimeError(
            "Browser não inicializado. Verifique o lifespan da aplicação."
        )
    return browser
