import inspect

from .version import __version__  # noqa
from .connection import MDCConnection
from .command import Command
from . import commands


class MDC(MDCConnection):
    _commands = {}

    @classmethod
    def register_command(cls, command):
        cls._commands[command.name] = command
        setattr(cls, command.name, command)


for name, cls in inspect.getmembers(commands, inspect.isclass):
    if (issubclass(cls, Command)
       and cls is not Command
       and not name.startswith('_')):
        MDC.register_command(cls())
