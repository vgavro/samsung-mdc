import inspect

from .connection import MDCConnection
from . import commands


class MDC(MDCConnection):
    _commands = {}

    @classmethod
    def register_command(cls, command):
        cls._commands[command.name] = command
        setattr(cls, command.name, command)


for name, cls in inspect.getmembers(commands, inspect.isclass):
    if issubclass(cls, commands._Command) and not name.startswith('_'):
        MDC.register_command(cls())
