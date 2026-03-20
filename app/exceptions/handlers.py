from fastapi.responses import JSONResponse
from app.config import logger
from .request_exception import WrongParams, ScrapError


async def validation_error_handler(request, exc):
    logger.warning(f"Validation error: {exc}")

    content_type = request.headers.get("content-type", "")

    if "application/json" not in content_type:
        return JSONResponse(
            status_code=415,
            content={
                "detail": "Formato de requisição inválido. Envie JSON com 'Content-Type: application/json'.",
                "example": {"cnpj": "00000000000000"},
            },
        )

    return JSONResponse(
        status_code=400,
        content={"detail": "Dados inválidos na requisição."},
    )


async def wrong_params_handler(request, exc: WrongParams):
    logger.warning(f"Wrong params: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def scrap_error_handler(request, exc: ScrapError):
    logger.error(f"Scrap error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error during scraping"},
    )


async def generic_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


__all__ = [
    "validation_error_handler",
    "wrong_params_handler",
    "scrap_error_handler",
    "generic_exception_handler",
    "WrongParams",
    "ScrapError",
]
