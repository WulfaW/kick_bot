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

        # Initialize Playwright for sending messages
        from playwright.async_api import async_playwright
        import os
        
        try:
            self.playwright = await async_playwright().start()
            cookies_file = "cookies.json"
            render_secrets_file = "/etc/secrets/cookies.json"
            cookies = None
            
            import json
            if os.path.exists(cookies_file):
                with open(cookies_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            elif os.path.exists(render_secrets_file):
                with open(render_secrets_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            elif os.getenv("KICK_COOKIES"):
                cookies = json.loads(os.getenv("KICK_COOKIES"))
                
            if cookies:
                # Docker ve düşük RAM ortamlarında Playwright'ın çökmesini engellemek için özel argümanlar
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
                
                # Playwright sameSite format uyumluluğu için küçük bir düzeltme
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
                
                # Open a separate page for each channel
                for channel in self.config.channels:
                    page = await self.context.new_page()
                    await page.goto(f"https://kick.com/{channel}")
                    self.pages[channel] = page
                    
                logger.info(f"Playwright headless browser started and loaded pages for channels: {self.config.channels}")
            else:
                logger.warning("cookies.json not found! Playwright sender will not work.")
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")

    async def send_message(self, channel: str, message: str):
        logger.info(f"[Kick -> {channel}] {message}")
        page = self.pages.get(channel)
        if page:
            try:
                # Find the chat input box (Kick uses an editor with contenteditable="true")
                editor = page.locator('div[contenteditable="true"]')
                # Wait for it to be ready
                await editor.wait_for(state="visible", timeout=15000)
                await editor.fill(message)
                
                # Sometime Kick has a "Chat" button, but pressing Enter inside the editor works
                await editor.press("Enter")
                logger.info(f"Message sent to {channel} physically via Playwright.")
            except Exception as e:
                title = await page.title()
                logger.error(f"Failed to send message to {channel} via Playwright. Error: {e} | Page Title: {title}")

    async def disconnect(self):
        logger.info("Disconnecting from Kick...")
        for task in self.listener_tasks:
            task.cancel()
            
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
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
