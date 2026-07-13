from bot.commands.base import BaseCommand
from bot.services.valorant import ValorantService
from bot.core.config import Config
from typing import List

class PeakCommand(BaseCommand):
    """
    Fetches the highest/peak Valorant MMR for a given user or the default user.
    """
    
    def __init__(self, valorant_service: ValorantService, config: Config):
        self.valorant_service = valorant_service
        self.config = config
        
    @property
    def name(self) -> str:
        return "peak"
        
    @property
    def aliases(self) -> List[str]:
        return ["highest", "maxrank"]
        
    async def execute(self, *args, **kwargs) -> str:
        name, tag = None, None
        
        if args and len(args) > 0:
            # Check if user typed: !peak Name#Tag
            if "#" in args[0]:
                parts = args[0].split("#", 1)
                name = parts[0]
                tag = parts[1]
                
        peak_data = await self.valorant_service.get_peak_mmr(name=name, tag=tag)
        
        if peak_data == "Could not fetch peak rank.":
            return peak_data
            
        return f"🏆 En Yüksek Rank: {peak_data}"
