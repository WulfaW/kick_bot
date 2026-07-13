import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class KickConfig:
    username: str
    channels: list[str]
    oauth: str

@dataclass
class RiotConfig:
    region: str
    name: str
    tag: str
    api_key: str
    crosshair: str

@dataclass
class Config:
    kick: KickConfig
    riot: RiotConfig

def load_config() -> Config:
    """
    Loads environment variables and populates the config dataclasses.
    """
    load_dotenv()
    
    channels_str = os.getenv("KICK_CHANNELS", os.getenv("KICK_CHANNEL", ""))
    channels_list = [c.strip() for c in channels_str.split(",") if c.strip()]
    
    kick_config = KickConfig(
        username=os.getenv("KICK_USERNAME", ""),
        channels=channels_list,
        oauth=os.getenv("KICK_OAUTH", "")
    )
    
    riot_config = RiotConfig(
        region=os.getenv("VAL_REGION", "eu"),
        name=os.getenv("RIOT_NAME", ""),
        tag=os.getenv("RIOT_TAG", ""),
        api_key=os.getenv("HENRIK_API_KEY", ""),
        crosshair=os.getenv("VAL_CROSSHAIR", "")
    )
    
    return Config(kick=kick_config, riot=riot_config)
