import asyncio

# Global state
browser = None
semaphore = asyncio.Semaphore(3)


async def get_tools():

    async with semaphore:
        context = None
        page = None
        try:
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            page = await context.new_page()
            yield page, context
        except Exception as e:
            print(e, flush=True)
            raise
        finally:
            await page.close() if page else None
            await context.close() if context else None
