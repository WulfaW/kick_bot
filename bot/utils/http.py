import aiohttp
import logging
import asyncio
from typing import Optional, Dict, Any
from .retry import async_retry

logger = logging.getLogger(__name__)

class HttpClient:
    """
    A persistent HTTP client wrapper using aiohttp with a built-in retry mechanism.
    """
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Initializes the aiohttp ClientSession."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self):
        """Closes the aiohttp ClientSession."""
        if self.session and not self.session.closed:
            await self.session.close()

    @async_retry(retries=3, delay=1.5, exceptions=(aiohttp.ClientError, asyncio.TimeoutError))
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> str:
        """
        Performs an asynchronous GET request. 
        Automatically retries on network failures or timeouts.
        """
        if not self.session:
            await self.start()
            
        logger.debug(f"Executing GET request to {url}")
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.text()
