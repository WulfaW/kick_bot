import asyncio
import logging
from typing import Callable, Any, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

def async_retry(retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    An asynchronous decorator that retries a function if specific exceptions occur.
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    logger.warning(f"Attempt {attempt}/{retries} failed for {func.__name__}: {e}")
                    if attempt >= retries:
                        logger.error(f"All {retries} attempts failed for {func.__name__}. Raising exception.")
                        raise
                    await asyncio.sleep(delay * attempt)
        return wrapper
    return decorator
