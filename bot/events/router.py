import logging
import importlib
import pkgutil
import inspect
from typing import Dict, Any

from bot.commands.base import BaseCommand

logger = logging.getLogger(__name__)

class CommandRouter:
    """
    Dynamically loads and routes incoming chat commands to their respective handlers.
    Implements a basic Dependency Injection mechanism for loaded commands.
    """
    def __init__(self, dependencies: Dict[str, Any]):
        self.commands: Dict[str, BaseCommand] = {}
        self.dependencies = dependencies
        self._load_commands()

    def _load_commands(self):
        """
        Dynamically imports all modules in the bot.commands package and registers
        any class inheriting from BaseCommand.
        """
        import bot.commands as commands_package
        
        for _, module_name, _ in pkgutil.iter_modules(commands_package.__path__):
            if module_name == "base":
                continue
            
            full_module_name = f"{commands_package.__name__}.{module_name}"
            module = importlib.import_module(full_module_name)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseCommand) and obj is not BaseCommand:
                    
                    # Inspect the constructor to inject required dependencies
                    init_signature = inspect.signature(obj.__init__)
                    kwargs = {}
                    
                    for param_name, param in init_signature.parameters.items():
                        if param_name == "self":
                            continue
                        
                        # Match dependency based on type annotation
                        for dep in self.dependencies.values():
                            if isinstance(dep, param.annotation) or param.annotation == Any:
                                kwargs[param_name] = dep
                                break
                                
                    try:
                        command_instance = obj(**kwargs)
                        self.register_command(command_instance)
                    except Exception as e:
                        logger.error(f"Failed to initialize command '{name}': {e}")

    def register_command(self, command: BaseCommand):
        """Registers a command and its aliases."""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
        logger.info(f"Registered command: !{command.name} (Aliases: {command.aliases})")

    async def handle_message(self, message: str) -> str | None:
        """
        Parses an incoming chat message and executes the mapped command if found.
        """
        if not message.startswith("!"):
            return None

        parts = message[1:].split()
        if not parts:
            return None

        command_name = parts[0].lower()
        args = parts[1:]
        if command_name in self.commands:
            logger.info(f"Executing command: !{command_name} with args: {args}")
            return await self.commands[command_name].execute(*args)
            
        return None
