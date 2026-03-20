from fastapi import FastAPI


def add_exceptions_handlers(app: FastAPI):
    from app.exceptions import (
        validation_error_handler,
        wrong_params_handler,
        scrap_error_handler,
        generic_exception_handler,
        WrongParams,
        ScrapError,
    )
    from pydantic import ValidationError
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(WrongParams, wrong_params_handler)
    app.add_exception_handler(ScrapError, scrap_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


def add_routes(app: FastAPI):
    from app.router import trabalhista, fgts, estadual, municipal

    app.include_router(trabalhista.router)
    app.include_router(fgts.router)
    app.include_router(estadual.router)
    app.include_router(municipal.router)


def add_middlewares(app: FastAPI):
    from app.config.middlewares import auth

    app.middleware("http")(auth)
