from playwright.async_api import async_playwright
from fastapi import FastAPI
from contextlib import asynccontextmanager
import app.utils.dependencies as deps
from app.config import HOST, PORT, RELOAD, HEADLESS, PLAYWRIGHT_ARGS, logger, setup_logging
from app.config import add_routes, add_exceptions_handlers, add_middlewares
from fastapi.staticfiles import StaticFiles

# Setup logging after config is fully loaded
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global playwright

    playwright = await async_playwright().start()
    deps.browser = await playwright.chromium.launch(
        args=PLAYWRIGHT_ARGS,
        headless=HEADLESS,
    )
    yield
    await deps.browser.close()
    await playwright.stop()


app = FastAPI(lifespan=lifespan)
app.mount("/public", StaticFiles(directory="public"), name="public")
add_routes(app)
add_exceptions_handlers(app)
add_middlewares(app)


if __name__ == "__main__":
    import uvicornd

    logger.info(f"Starting server on {HOST}:{PORT} with reload={RELOAD}")
    uvicorn.run("app.app:app", host=HOST, port=PORT, reload=RELOAD)


