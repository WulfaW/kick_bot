from bot.commands.base import BaseCommand
from bot.services.valorant import ValorantService

class RankCommand(BaseCommand):
    """
    Handles the !rank command.
    """
    def __init__(self, valorant_service: ValorantService):
        self.valorant_service = valorant_service

    @property
    def name(self) -> str:
        return "rank"

    @property
    def aliases(self) -> list[str]:
        return ["mmr", "elo"]

    async def execute(self, *args, **kwargs) -> str:
        name, tag = None, None
        
        if args and len(args) > 0:
            # Check if user typed: !rank Name#Tag
            if "#" in args[0]:
                parts = args[0].split("#", 1)
                name = parts[0]
                tag = parts[1]
                
        rank_data = await self.valorant_service.get_rank(name=name, tag=tag)
        
        if rank_data == "Could not fetch current rank.":
            return rank_data
            
        return f"🎯 Güncel Rank: {rank_data}"
