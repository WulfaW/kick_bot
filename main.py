import asyncio
import logging
import signal
import sys

from bot.core.config import load_config
from bot.utils.http import HttpClient
from bot.services.valorant import ValorantService
from bot.events.router import CommandRouter
from bot.adapters.kick_adapter import KickAdapter

# Setup Python logging instead of print()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("kick-bot")

async def main():
    logger.info("Starting Kick Bot...")

    # 1. Load configuration from .env
    config = load_config()

    # 2. Setup reusable HTTP Client
    http_client = HttpClient(timeout=10)
    await http_client.start()

    # 3. Initialize Services
    valorant_service = ValorantService(http_client, config.riot)

    # 4. Dependency Container (Manual DI setup)
    dependencies = {
        "config": config,
        "http_client": http_client,
        "valorant_service": valorant_service
    }

    # 5. Initialize dynamic Command Router
    router = CommandRouter(dependencies)

    # 6. Initialize Platform Adapter (Kick)
    kick_adapter = KickAdapter(config.kick)
    kick_adapter.register_message_handler(router.handle_message)

    # Setup Graceful Shutdown (captures CTRL+C and Docker stop signals)
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown():
        logger.info("Shutdown signal received. Exiting gracefully...")
        stop_event.set()

    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown)
    else:
        # On Windows, we rely on the try/except KeyboardInterrupt in the __main__ block
        # However, to simulate graceful shutdown internally, we can still use stop_event
        pass

    # 7. Connect to Chat Platform
    await kick_adapter.connect()

    # ========================================================
    # RENDER FIX: Start a dummy web server to satisfy the port scan
    # ========================================================
    from aiohttp import web
    async def health_check(request):
        return web.Response(text="Bot is running!")
    
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    import os
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Dummy web server started on port {port} to satisfy Render.")

    # ========================================================
    # Bot is now listening to real Kick chat events.
    # It will block here until a shutdown signal is received.
    # ========================================================
    await stop_event.wait()

    # 8. Cleanup and Teardown
    await site.stop()
    await runner.cleanup()
    await kick_adapter.disconnect()
    await http_client.close()
    logger.info("Bot shut down successfully.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Prevent noisy traceback on CTRL+C during startup
        pass
