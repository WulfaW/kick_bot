from abc import ABC, abstractmethod
from typing import List

class BaseCommand(ABC):
    """
    Abstract base class for all bot commands.
    Enforces a consistent interface for the Command Router.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (e.g., 'rank'). Do not include the prefix."""
        pass

    @property
    @abstractmethod
    def aliases(self) -> List[str]:
        """List of alternative command names (aliases)."""
        pass

    @abstractmethod
    async def execute(self, *args, **kwargs) -> str:
        """
        Executes the command logic.
        Returns the string response to be sent back to the chat.
        """
        pass
