import logging
import asyncio
from bot.adapters.base import BaseAdapter
from bot.core.config import KickConfig

logger = logging.getLogger(__name__)

class KickAdapter(BaseAdapter):
    """
    Adapter implementation for Kick chat using kickpython wrapper.
    Supports multiple channels simultaneously.
    """
    def __init__(self, config: KickConfig):
        super().__init__()
        self.config = config
        
        from kickpython.api import KickAPI
        # Create a separate KickAPI instance per channel
        self.apis = {channel: KickAPI() for channel in self.config.channels}
        self.listener_tasks = []
        self.pages = {}
        self.playwright = None
        self.browser = None
        self.context = None

    async def connect(self):
        logger.info(f"Connecting to Kick channels: {self.config.channels}...")
        
        for channel, api in self.apis.items():
            
            def create_handler(ch):
                async def handler(message: dict):
                    try:
                        content = message.get("content", "")
                        if not content:
                            return

                        sender = message.get("sender", {}).get("username", "Unknown")
                        logger.info(f"[Kick <- {ch}] {sender}: {content}")
                        
                        if self.on_message_handler:
                            response = await self.on_message_handler(content)
                            if response:
                                await self.send_message(ch, response)
                    except Exception as e:
                        logger.error(f"Error handling message for {ch}: {e}")
                return handler

            api.add_message_handler(create_handler(channel))
            self.listener_tasks.append(
                asyncio.create_task(api.start_chat_listener(channel))
            )
        
        logger.info("Connected to Kick channels via kickpython wrappers.")
        await self._init_playwright()

    async def _cleanup_playwright(self):
        logger.info("Cleaning up Playwright resources...")
        self.pages.clear()
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.debug(f"Error closing browser during cleanup: {e}")
        finally:
            self.browser = None

        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.debug(f"Error stopping playwright during cleanup: {e}")
        finally:
            self.playwright = None
            
        self.context = None

    async def _init_playwright(self):
        from playwright.async_api import async_playwright
        import os
        import json
        
        logger.info("Initializing Playwright...")
        await self._cleanup_playwright()
        
        try:
            self.playwright = await async_playwright().start()
            cookies_file = "cookies.json"
            render_secrets_file = "/etc/secrets/cookies.json"
            cookies = None
            
            if os.path.exists(cookies_file):
                with open(cookies_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            elif os.path.exists(render_secrets_file):
                with open(render_secrets_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            elif os.getenv("KICK_COOKIES"):
                cookies = json.loads(os.getenv("KICK_COOKIES"))
                
            if cookies:
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-software-rasterizer"
                    ]
                )
                self.context = await self.browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                )
                
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']:
                        del c['sameSite']
                    if 'hostOnly' in c:
                        del c['hostOnly']
                    if 'session' in c:
                        del c['session']
                    if 'storeId' in c:
                        del c['storeId']
                    if 'partitionKey' in c:
                        del c['partitionKey']
                    if 'expirationDate' in c:
                        c['expires'] = c['expirationDate']
                        del c['expirationDate']
                        
                await self.context.add_cookies(cookies)
                
                from playwright_stealth import Stealth
                for channel in self.config.channels:
                    page = await self.context.new_page()
                    await Stealth().apply_stealth_async(page)
                    await page.goto(f"https://kick.com/{channel}")
                    await page.wait_for_timeout(5000)
                    self.pages[channel] = page
                    
                logger.info(f"Playwright headless browser started and loaded pages for channels: {self.config.channels}")
            else:
                logger.warning("cookies.json not found! Playwright sender will not work.")
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")

    async def send_message(self, channel: str, message: str):
        safe_msg = message.encode('ascii', 'ignore').decode('ascii')
        logger.info(f"[Kick -> {channel}] {safe_msg}")
        
        # Check connection status
        is_connected = False
        try:
            if self.browser:
                is_conn = self.browser.is_connected
                is_connected = is_conn() if callable(is_conn) else is_conn
        except Exception:
            is_connected = False
            
        page = self.pages.get(channel)
        if not page or not is_connected:
            logger.warning(f"Browser or page for {channel} is disconnected or crashed. Restarting Playwright...")
            await self._init_playwright()
            page = self.pages.get(channel)
            
        if page:
            try:
                editor = page.locator('div[contenteditable="true"]')
                await editor.wait_for(state="visible", timeout=15000)
                await editor.fill(message)
                await editor.press("Enter")
                logger.info(f"Message sent to {channel} physically via Playwright.")
            except Exception as e:
                logger.error(f"Failed to send message to {channel} via Playwright. Error: {e}")
                # Trigger clean up so it restarts on next message
                if "Target crashed" in str(e) or "Connection closed" in str(e):
                    logger.warning("Target crashed or connection closed. Cleaning up for restart...")
                    await self._cleanup_playwright()

    async def disconnect(self):
        logger.info("Disconnecting from Kick...")
        for task in self.listener_tasks:
            task.cancel()
            
        await self._cleanup_playwright()
            
        for api in self.apis.values():
            if hasattr(api, 'close'):
                if asyncio.iscoroutinefunction(api.close):
                    await api.close()
                else:
                    api.close()
                
    async def simulate_incoming_message(self, channel: str, message: str):
        """Simulate a message when KickAPI is unavailable for testing."""
        logger.info(f"[SIMULATED Kick <- {channel}] {message}")
        if self.on_message_handler:
            response = await self.on_message_handler(message)
            if response:
                await self.send_message(channel, response)
