import secrets
from playwright.async_api import async_playwright
from fastapi import FastAPI, Request
import pytz
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.router import trabalhista, fgts, estadual, municipal
import app.utils.dependencies as deps
from fastapi.responses import JSONResponse
import os


load_dotenv()
tz = pytz.timezone("America/Sao_Paulo")
playwright = None
SECRET_KEY = os.environ.get("SECRET_KEY")


if not any([SECRET_KEY, os.environ.get("CAPTCHA_API_KEY")]):
    raise Exception("SECRET_KEY is required in environment variables")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global playwright

    playwright = await async_playwright().start()
    deps.browser = await playwright.chromium.launch(
        args=[
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
        ],
        headless=False,
    )
    yield
    await deps.browser.close()
    await playwright.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(trabalhista.router)
app.include_router(fgts.router)
app.include_router(estadual.router)
app.include_router(municipal.router)


@app.middleware("http")
async def dunno(request: Request, call_next):
    try:
        if request.method != "GET":
            auth = request.headers.get("Authorization")

            if not auth or not auth.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authorization header ausente ou inválido"},
                )

            token = auth.split(" ")[1]

            if not secrets.compare_digest(token, SECRET_KEY):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token de autenticação inválido"},
                )
        response = await call_next(request)

        return response
    except Exception as e:
        print(e, flush=True)
        return {"status": 500, "message": "couldnt complete scrap"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.app:app", host="0.0.0.0", port=5000, reload=False)
