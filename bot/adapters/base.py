from abc import ABC, abstractmethod
from typing import Callable, Awaitable

class BaseAdapter(ABC):
    """
    Abstract interface for Chat Platform Adapters.
    Decouples the core bot logic from the specific chat provider.
    """
    def __init__(self):
        self.on_message_handler: Callable[[str], Awaitable[str | None]] | None = None

    def register_message_handler(self, handler: Callable[[str], Awaitable[str | None]]):
        """Registers the callback function to handle incoming chat messages."""
        self.on_message_handler = handler

    @abstractmethod
    async def connect(self):
        """Establish connection to the chat server."""
        pass

    @abstractmethod
    async def send_message(self, channel: str, message: str):
        """Send a message to a specific channel/chat."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the chat server gracefully."""
        pass
