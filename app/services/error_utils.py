from playwright.async_api import Page
from app.exceptions import ScrapError
from app.config import logger


def raise_timeout(service: str, cnpj: str, page: Page, error: Exception) -> None:
    logger.error(f"{service} timeout for CNPJ {cnpj}: {error}")
    raise ScrapError(f"Timeout durante consulta {service} para {cnpj}")


def raise_unexpected(service: str, cnpj: str, page: Page, error: Exception) -> None:
    logger.error(f"{service} scrape error: {error}")
    raise ScrapError(f"Erro inesperado no scraping {service} para {cnpj}: {str(error)}")
