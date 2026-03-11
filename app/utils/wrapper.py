from functools import wraps
from app.config import logger
from app.exceptions import WrongParams


def handle_scraping_request(func):
    """Decorator for scraping route handlers - handles errors and logging"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except WrongParams as e:
            logger.warning(f"Wrong params: {e}")
            raise
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
    return wrapper


