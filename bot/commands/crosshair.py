from bot.commands.base import BaseCommand
from bot.core.config import Config

class CrosshairCommand(BaseCommand):
    """
    Handles the !crosshair command to show the streamer's crosshair.
    """
    def __init__(self, config: Config):
        self.config = config

    @property
    def name(self) -> str:
        return "crosshair"

    @property
    def aliases(self) -> list[str]:
        return ["cross", "ch"]

    async def execute(self, *args, **kwargs) -> str | None:
        crosshair_code = self.config.riot.crosshair
        if not crosshair_code:
            return None
        return f"🎯 Crosshair Kodu: {crosshair_code}"
