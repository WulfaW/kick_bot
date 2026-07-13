import logging
import json
from bot.utils.http import HttpClient
from bot.core.config import RiotConfig

logger = logging.getLogger(__name__)

class ValorantService:
    """
    Service responsible for interacting with external Valorant/Riot APIs.
    """
    def __init__(self, http_client: HttpClient, config: RiotConfig):
        self.http_client = http_client
        self.config = config
        self.base_url = "https://api.henrikdev.xyz/valorant/v2/mmr"

    async def get_rank(self, name: str = None, tag: str = None) -> str:
        """
        Fetches the current rank of the configured or specified Valorant player.
        """
        if not self.config.api_key:
            return "Lütfen .env dosyasında HENRIK_API_KEY değerini belirleyin."

        target_name = name if name else self.config.name
        target_tag = tag if tag else self.config.tag

        url = f"{self.base_url}/{self.config.region}/{target_name}/{target_tag}"
        headers = {"Authorization": self.config.api_key}
        
        try:
            response_text = await self.http_client.get(url, headers=headers)
            data = json.loads(response_text)
            
            if data.get("status") == 200:
                mmr_data = data.get("data", {}).get("current_data", {})
                rank_name = mmr_data.get("currenttierpatched", "Unranked")
                rr = mmr_data.get("ranking_in_tier", 0)
                return f"{rank_name} - {rr}RR"
            else:
                logger.error(f"API Error: {data}")
                return "Could not fetch current rank."
                
        except Exception as e:
            logger.error(f"Failed to fetch Valorant rank for {target_name}#{target_tag}: {e}")
            return "Could not fetch current rank."

    async def get_peak_mmr(self, name: str = None, tag: str = None) -> str:
        """Fetch peak rank for a player."""
        target_name = name if name else self.config.name
        target_tag = tag if tag else self.config.tag

        url = f"{self.base_url}/{self.config.region}/{target_name}/{target_tag}"
        headers = {"Authorization": self.config.api_key}
        
        try:
            response_text = await self.http_client.get(url, headers=headers)
            data = json.loads(response_text)
            peak_data = data.get("data", {}).get("highest_rank", {})
            if not peak_data:
                return "Peak rank not found."
                
            peak_tier = peak_data.get("patched_tier", "Unranked")
            season = peak_data.get("season", "Unknown")
            return f"{peak_tier} (Bölüm: {season.upper()})"
        except Exception as e:
            logger.error(f"Failed to fetch peak rank for {target_name}#{target_tag}: {e}")
            return "Could not fetch peak rank."
