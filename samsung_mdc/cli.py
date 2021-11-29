# NOTE: This module is hacking some internals of "click" library
# and may not work stable in case of click major changes in future versions.
# Tested with click==7.1.2

# BEWARE: If you want something flexible and overridable for cli processing,
# "click" just may not be your choice...

from datetime import time, datetime
from enum import Enum
import asyncio
import re
import os.path
from sys import argv as sys_argv
import platform

import click

from . import MDC, fields, __version__
from .utils import parse_hex, repr_hex
from .exceptions import NAKError


def _parse_int(x):
    return int(x, 16) if x.startswith('0x') else int(x)


def _repr(val, root=True):
    if isinstance(val, list):
        # quickfix for script command repr
        # maybe this should better be fixed in create_mdc_call
        return ' '.join(_repr(x, root) for x in val)
    if isinstance(val, tuple):
        return (' ' if root else ',').join(_repr(x, False) for x in val)
    if isinstance(val, (datetime, time)):
        return val.isoformat()
    elif isinstance(val, Enum):
        return f'<{val.__class__.__name__}.{val.name}:{val.value}>'
    return str(val)


def trim_docstring(docstring):
    # from https://www.python.org/dev/peps/pep-0257/
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = 1024
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < 1024:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


class EnumChoice(click.ParamType):
    # This is not part of a click because of... WTF?
    # https://github.com/pallets/click/issues/605
    # All proposals in ticket are bad anyway, so impementing
    # another one...
    name = 'enum_choice'

    def __init__(self, enum):
        self.enum = enum

    def get_metavar(self, param):
        return f'{self.enum.__name__}'

    def get_missing_message(self, param):
        return "Choose from:\n\t{}.".format(",\n\t".join(
            self.enum.__members__))

    def convert(self, value, param, ctx):
        if value.upper() in self.enum.__members__:
            return self.enum[value.upper()]
        else:
            # NOTE: Specific part for this project...
            # not sure how to make it more universal
            try:
                value = _parse_int(value)
            except ValueError:
                pass

            if value in [v.value for v in self.enum]:
                return value
        missing_message = self.get_missing_message(param)
        self.fail(f"Invalid choice: {value}\n{missing_message}")

    def __repr__(self):
        return f"EnumChoice({self.enum})"


class EnumTuple(EnumChoice):
    name = "enum_tuple"

    def convert(self, value, param, ctx):
        if not value:
            return tuple()
        convert_ = super().convert
        return tuple(convert_(v, param, ctx)
                     for v in value.split(','))

    def __repr__(self):
        return f"EnumTuple({self.enum})"


class Time(click.ParamType):
    name = "time"

    def convert(self, value, param, ctx):
        try:
            return time(*map(int, value.split(':')))
        except ValueError:
            self.fail("{} is not a valid time".format(value), param, ctx)

    def __repr__(self):
        return "TIME"


class ArgumentWithHelp(click.Argument):
    # Extends Argument with "help" parameter,
    # so they can be rendered in help same way as options
    # See ArgumentWithHelpCommandMixin
    def __init__(self, *args, help=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = help


class ArgumentWithHelpCommandMixin:
    def __init__(self, *args, help_arguments_label='Arguments', **kwargs):
        self.help_arguments_label = help_arguments_label
        super().__init__(*args, **kwargs)

    def format_arguments(self, ctx, formatter):
        args = []
        for param in self.get_params(ctx):
            if isinstance(param, click.Argument):
                help = getattr(param, 'help', None)
                args.append((param.metavar or param.name, help or ''))
        if args:
            with formatter.section(self.help_arguments_label):
                formatter.write_dl(args)

    def format_options(self, ctx, formatter):
        # Override this to format ArgumentWithHelp before options
        self.format_arguments(ctx, formatter)
        super().format_options(ctx, formatter)


class FixedSubcommand(ArgumentWithHelpCommandMixin, click.Command):
    # This mixin contains some common overrides and fixes for click
    # subcommand processing

    def parse_args(self, ctx, args):
        # Avoid "Try 'samsung-mdc {command} --help' for help." message
        # that renders in UsageError,
        # because it's wrong command because of required group command args
        # (maybe this will be fixed in future click versions?)
        try:
            super().parse_args(ctx, args)
        except click.UsageError as exc:
            exc.cmd = None
            raise

    def format_usage(self, ctx, formatter):
        # 1. Invoking this on subcommand doesn't show group required arguments
        # and options, so Usage is no valid in this case.
        # 2. Invoking this on wrong context mess things up completely,
        # but we need it from group context to be able to do
        # "samsung-mdc --help command1"
        # NOTE: this works only on 1-st level subcommand, for nesting
        # you may want to make root parts recursive
        root_path = ctx.command_path.split()[0]
        root_command = ctx.parent and ctx.parent.command or ctx.command
        pieces = click.Command.collect_usage_pieces(root_command, ctx)
        pieces.append(self.name)
        pieces.extend(self.collect_usage_pieces(ctx))
        formatter.write_usage(root_path, " ".join(pieces))


class Group(click.Group):
    def get_help_option(self, ctx):
        # Override this to pass parameters to --help
        # This is needed to be able to do "--help COMMAND"
        # without group required arguments
        def show_help(ctx, param, value):
            if value and not ctx.resilient_parsing:
                # Match registered commands and show help for all of them
                commands = [
                    ctx.command.commands[name]
                    for name in sys_argv[1:]
                    if name in ctx.command.commands
                ]
                if commands:
                    for i, command in enumerate(commands):
                        if i:
                            click.echo()
                        click.echo(f'Command: {command.name}')
                        click.echo(command.get_help(ctx), color=ctx.color)
                    ctx.exit()
                else:
                    # Show default help if no commands were matched
                    click.echo(ctx.get_help(), color=ctx.color)
                    ctx.exit()

        return click.Option(
            ['-h', '--help'],
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=show_help,
            help="Show this message and exit.",
        )

    def list_commands(self, ctx):
        # Avoid sorting commands by name, sort by CMD code instead
        # (as it goes in documentation)

        def key(c):
            # not mdc commands ("script") should go last
            return (hasattr(c, 'mdc_command')
                    and c.mdc_command.get_order() or (1000,))

        return [c.name for c in sorted(self.commands.values(), key=key)]


class MDCClickCommand(FixedSubcommand):
    def __init__(self, name, mdc_command, **kwargs):
        self.mdc_command = mdc_command
        name = mdc_command.name
        kwargs['short_help'] = self._get_params_hint()
        if not mdc_command.SET:
            kwargs['short_help'] = f'({kwargs["short_help"]})'
        kwargs['help_arguments_label'] = 'Data'
        kwargs['help'] = trim_docstring(mdc_command.__doc__)

        # Registering params from DATA format
        kwargs.setdefault('params', [])

        if isinstance(mdc_command.CMD, fields.Field):
            kwargs['params'].append(
                self._get_argument_from_mdc_field(mdc_command.CMD, 'cmd'))

        for i, field in enumerate(mdc_command.DATA):
            kwargs['params'].append(
                self._get_argument_from_mdc_field(field, i))

        super().__init__(name, **kwargs)

    def format_arguments(self, ctx, formatter):
        super().format_arguments(ctx, formatter)
        if getattr(self.mdc_command, 'RESPONSE_EXTRA', []):
            args = [
                self._get_argument_from_mdc_field(field)
                for field in self.mdc_command.RESPONSE_EXTRA
            ]
            with formatter.section('Response extra'):
                formatter.write_dl((
                    param.metavar or param.name, getattr(param, 'help', '')
                ) for param in args)

    def _get_argument_from_mdc_field(self, field, ident=None):
        if isinstance(field, fields.Bitmask):
            type = EnumTuple(field.enum)
            help = ('list(,) ' +
                    (' | '.join(field.enum.__members__.keys())))
        elif isinstance(field, fields.Enum):
            type = EnumChoice(field.enum)
            help = ' | '.join(field.enum.__members__.keys())
        elif isinstance(field, fields.DateTime):
            formats = [
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M",
            ]
            type = click.DateTime(formats)
            help = f'datetime (format: {" / ".join(formats)})'
        elif isinstance(field, (fields.Time, fields.Time12H)):
            type = Time()
            help = 'time (format: %H:%M:%S)'
        elif isinstance(field, fields.IPAddress):
            type = str
            help = 'IP address'
        elif isinstance(field, fields.VideoWallModel):
            type = str
            help = 'Video Wall model (format: X,Y eg. 4,5)'
        else:
            type = {
                fields.Str: str,
                fields.Bool: bool,
                fields.Int: int,
            }[field.__class__]
            help = type.__name__.lower()
            if type is int and field.range:
                help += f' ({field.range.start}-{field.range.stop - 1})'

        return ArgumentWithHelp(
            [f'data_{ident}' if ident else field.name],
            metavar=field.name, type=type, help=help)

    def _get_params_hint(self):
        params = ' '.join([f.name for f in self.mdc_command.DATA])
        if self.mdc_command.GET and self.mdc_command.SET and params:
            params = f'[{params}]'
        if isinstance(self.mdc_command.CMD, fields.Field):
            # parametrized CMD is always required argument
            params = f'{self.mdc_command.CMD.name} {params}'
        return params

    def collect_usage_pieces(self, ctx):
        # We need ALL arguments to be OR optional, OR required,
        # so we can't use required on arguments and need to show
        # it properly in usage string
        if self.mdc_command.SET:
            return [self._get_params_hint()]
        return []

    def parse_args(self, ctx, args):
        # We need ALL arguments to be OR optional, OR required,
        # so if there is no arguments supplied - this is proper
        # GET command

        # Except parametrized CMD - special case for timer,
        # we have 14 almost identical commands otherwise...
        if isinstance(self.mdc_command.CMD, fields.Field):
            if self.mdc_command.GET and len(args) == 1:
                if '--help' in sys_argv:
                    return super().parse_args(ctx, args)

                parser = self.make_parser(ctx)
                opts, args, param_order = parser.parse_args(args=args)
                for param in self.get_params(ctx):
                    value, args = param.handle_parse_result(
                        ctx, opts, args)
                    break  # after first argument

                ctx.args = args
                return

        elif not args and self.mdc_command.GET:
            ctx.args = args
            return args

        try:
            super().parse_args(ctx, args)
        except click.UsageError as exc:
            # Avoid parameters validation on GET-only commands
            if not self.mdc_command.SET:
                exc = click.UsageError('Readonly command doesn\'t accept '
                                       'any arguments', ctx)
                exc.cmd = None  # see FixedSubcommand for reason
                raise exc
            raise

    def create_mdc_call(self, params):
        args = tuple(params.values())
        if isinstance(self.mdc_command.CMD, fields.Field):
            args = args[0], args[1:]
        else:
            args = [args] if args else []

        if args and not self.mdc_command.SET:
            raise click.UsageError('Readonly command doesn\'t accept '
                                   'any arguments')

        async def mdc_call(connection, display_id):
            try:
                print(f'{display_id}@{connection.target}',
                      _repr(await self.mdc_command(connection, display_id,
                                                   *args)))
            except Exception as exc:
                print(f'{display_id}@{connection.target}',
                      f'{exc.__class__.__name__}: {exc}')
                raise
        mdc_call.name = self.name
        mdc_call.args = args
        return mdc_call


class MDCTargetParamType(click.ParamType):
    name = 'mdc_target'

    _win_com_port_regexp = re.compile(r'COM\d+', re.IGNORECASE)

    # def get_missing_message(self, param):
    #     return param.help

    def convert_target(self, value, param, ctx):
        if '@' not in value:
            self.fail('DISPLAY_ID required (try 0, 1)')

        display_id, addr = value.split('@')
        try:
            display_id = _parse_int(display_id)
        except ValueError:
            self.fail(
                f'Invalid DISPLAY_ID "{display_id}" '
                '(int or hex, example: 1, 0x01, 254, 0xFE)')
        if ':' in addr:
            ip, port = addr.split(':')
            try:
                port = int(port)
            except ValueError:
                self.fail(f'Invalid PORT "{port}"')
            return 'tcp', f'{ip}:{port}', display_id
        elif (
            '/' in addr or addr.startswith('.')
            or self._win_com_port_regexp.match(addr)
        ):
            return 'serial', addr, display_id
        return 'tcp', addr, display_id

    def convert(self, value, param, ctx):
        if '@' in value:
            return [self.convert_target(value, param, ctx)]
        elif (
            self._win_com_port_regexp.match(value)
            or value.startswith('/dev/')
        ):
            self.fail('Looks like you want to use serial port, '
                      'but DISPLAY_ID required (try 0, 1)')
        else:
            if not os.path.exists(value):
                self.fail(f'FILENAME "{value}" does not exist.')
            data = open(value).read()
            data = [
                (i + 1, line.strip())
                for i, line in enumerate(data.split('\n'))
                if line.strip() and not line.strip().startswith('#')
            ]
            targets = []
            for lineno, line in data:
                try:
                    targets.append(self.convert_target(line, param, ctx))
                except click.UsageError as exc:
                    exc.message = (f'{value}:{lineno}: "{line}": '
                                   f'{exc.message}')
                    raise
            if not targets:
                self.fail(
                    f'FILENAME "{value} is empty.')
            return targets


MAIN_HELP = """
Try 'samsung-mdc --help COMMAND' for command info\n
For multiple targets commands will be running async,
so result order may differ.

TARGET may be:

\b
DISPLAY_ID@IP[:PORT] (default port: 1515, example: 0@192.168.0.10:1515)
FILENAME with target list (separated by newline)

\b
For serial port connection:
DISPLAY_ID@PORT_NAME for Windows (example: 1@COM1)
DISPLAY_ID@PORT_PATH (example: 1@/dev/ttyUSB0)

We're trying to make autodetection of connection mode by port name,
but you may want to use --mode option.
"""


@click.group(cls=Group, help=MAIN_HELP)
@click.version_option(version=__version__)
@click.argument('target', metavar='TARGET',
                type=MDCTargetParamType())
@click.option('-v', '--verbose', is_flag=True, default=False, type=bool)
@click.option('-m', '--mode', default='auto', help='default: auto',
              type=click.Choice(('auto', 'tcp', 'serial'),
                                case_sensitive=False))
@click.option('-p', '--pin', default=None, type=int,
              help='4-digit PIN for secured TLS connection. '
                   'If PIN provided, "Secured Protocol" must be enabled '
                   'on remote device.')
@click.option(
    '-t', '--timeout', default=5, type=float, help=(
        'read/write/connect timeout in seconds (default: 5) '
        '(connect can be overridden with separate option)'))
@click.option('--connect-timeout', default=None, type=float)
@click.pass_context
def cli(ctx, target, verbose, mode, pin, **kwargs):
    ctx.ensure_object(dict)
    ctx.obj['targets'] = [(
        MDC(target, auto_mode if mode == 'auto' else mode,
            **{'verbose': verbose, 'pin': pin, **kwargs}),
        display_id
    ) for auto_mode, target, display_id in target]
    ctx.obj['verbose'] = verbose


def asyncio_run(call, targets):
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([
        loop.create_task(call(*target))
        for target in targets
    ]))

    # Gracefully close connections
    connections = [target[0] for target in targets if target[0].is_opened]
    if connections:
        loop.run_until_complete(asyncio.wait([
            loop.create_task(connection.close())
            for connection in connections
        ]))

    loop.close()


def register_command(command):
    @click.pass_context
    def _cmd(ctx, **kwargs):
        mdc_call = ctx.command.create_mdc_call(kwargs)
        failed_targets = []

        async def call(connection, display_id):
            try:
                await mdc_call(connection, display_id)
            except Exception as exc:
                failed_targets.append((connection, display_id, exc))
                if ctx.obj['verbose']:
                    raise

        asyncio_run(call, ctx.obj['targets'])

        if failed_targets:
            if len(ctx.obj['targets']) > 1:
                print('Failed targets:', len(failed_targets))
            ctx.exit(1)

    cli.command(cls=MDCClickCommand, mdc_command=command)(_cmd)


for command in MDC._commands.values():
    register_command(command)


SCRIPT_HELP = """
Script file with commands to execute.

Commands for multiple targets will be running async, but
commands order is preserved for device (and is running on same connection),
exit on first fail unless retry options provided.

It\'s highly recommended to use sleep option for virtual_remote!

\b
Additional commands:
sleep SECONDS  (FLOAT, --sleep option for this command is ignored)
disconnect

\b
Format:
command1 [ARGS]...
command2 [ARGS]...

\b
Example: samsung-mdc ./targets.txt script -s 3 -r 1 ./commands.txt
# commands.txt content
power on
sleep 5
clear_menu
virtual_remote key_menu
virtual_remote key_down
virtual_remote enter
clear_menu
"""


@cli.command(help=SCRIPT_HELP, cls=FixedSubcommand)
@click.option('-s', '--sleep', default=0, type=float,
              help='Pause between commands (seconds)')
@click.option('--retry-command', default=0, type=int,
              help='Retry command if failed (count)')
@click.option('--retry-command-sleep', default=0, type=float,
              help='Sleep before command retry (seconds)')
@click.option('-r', '--retry-script', default=0, type=int,
              help='Retry script if failed (count)')
@click.option('--retry-script-sleep', default=0, type=float,
              help='Sleep before script retry (seconds)')
@click.option('--ignore-nak', is_flag=True,
              help='Ignore negative acknowledgement errors')
@click.argument('script_file', type=click.File(),
                help='Text file with commands, separated by newline.',
                cls=ArgumentWithHelp)
@click.pass_context
def script(ctx, script_file, sleep, retry_command, retry_command_sleep,
           retry_script, retry_script_sleep, ignore_nak):
    import shlex

    retry_command_sleep = retry_command_sleep or sleep
    retry_script_sleep = retry_script_sleep or sleep

    def fail(lineno, line, reason):
        raise click.UsageError(
            f'{script_file.name}:{lineno}: "{line}": {reason}')

    def create_disconnect():
        async def disconnect(connection, display_id):
            await connection.close()
            return tuple()
        disconnect.name = 'disconnect'
        disconnect.args = []
        return disconnect

    def create_sleep(seconds):
        async def sleep(connection, display_id):
            await asyncio.sleep(seconds)
            return tuple()
        sleep.name = 'sleep'
        sleep.args = [seconds]
        return sleep

    lines = [
        (i + 1, line.strip())
        for i, line in enumerate(script_file.read().split('\n'))
        if line.strip() and not line.strip().startswith('#')
    ]
    calls = []
    for lineno, line in lines:
        command, *args = shlex.split(line)
        command = command.lower()
        if (command not in cli.commands
           and command not in ['sleep', 'disconnect']):
            fail(lineno, line, f'Unknown command: {command}')
        if command == 'sleep':
            if len(args) != 1:
                fail(lineno, line, 'Sleep command accept exactly one argument')
            try:
                seconds = float(args[0])
            except ValueError as exc:
                fail(lineno, line, f'Sleep argument must be int/float: {exc}')
            calls.append(create_sleep(seconds))
        elif command == 'disconnect':
            if len(args):
                fail(lineno, line, 'Disconnect command does not accept '
                     'arguments')
            calls.append(create_disconnect())
        else:
            ctx.params.clear()
            command = cli.commands[command]
            try:
                command.parse_args(ctx, args)
            except click.UsageError as exc:
                fail(lineno, line, str(exc))
            calls.append(command.create_mdc_call(ctx.params))

    failed_targets = []

    async def call(connection, display_id):
        last_exc = None
        for retry_script_i in range(retry_script + 1):
            if retry_script_i and retry_script_sleep:
                await asyncio.sleep(retry_script_sleep)
            for command_i, call_ in enumerate(calls):
                if command_i and call_.name != 'sleep' and sleep:
                    await asyncio.sleep(sleep)
                for retry_command_i in range(retry_command + 1):
                    if retry_command_i and retry_command_sleep:
                        await asyncio.sleep(retry_command_sleep)
                    if ctx.obj['verbose']:
                        print(
                            f'{display_id}@{connection.target}',
                            f'{retry_script_i}:{command_i}:{retry_command_i}',
                            f'{call_.name} {_repr(call_.args)}')
                    try:
                        await call_(connection, display_id)
                    except Exception as exc:
                        if ignore_nak and isinstance(exc, NAKError):
                            last_exc = None
                            break
                        last_exc = exc
                    else:
                        last_exc = None
                        break
                if last_exc is not None:
                    break
            if last_exc is None:
                break

        if last_exc is not None:
            failed_targets.append((connection, display_id, last_exc))
            print(f'{display_id}@{connection.target}',
                  f'Script failed indefinitely: {last_exc}')
            if ctx.obj['verbose']:
                raise last_exc

    asyncio_run(call, ctx.obj['targets'])

    if failed_targets:
        if len(ctx.obj['targets']) > 1:
            print('Failed targets:', len(failed_targets))
        ctx.exit(1)


@cli.command(help='Helper command to send raw data for test purposes.',
             cls=FixedSubcommand)
@click.argument(
    'command', type=str, cls=ArgumentWithHelp,
    help='Command and (optionally) subcommand (example: a1 or a1:b2)')
@click.argument(
    'data', type=str, default='', cls=ArgumentWithHelp,
    help='Data payload if any (example: a1:b2)')
@click.pass_context
def raw(ctx, command, data):
    failed_targets = []

    async def call(connection, display_id):
        try:
            ack, rcmd, resp_data = await connection.send(
                tuple(parse_hex(command)), display_id,
                parse_hex(data))
            print(
                f'{display_id}@{connection.target}',
                'A' if ack else 'N', repr_hex(rcmd), repr_hex(resp_data)
            )

        except Exception as exc:
            print(f'{display_id}@{connection.target}',
                  f'{exc.__class__.__name__}: {exc}')
            failed_targets.append((connection, display_id, exc))
            if ctx.obj['verbose']:
                raise

    asyncio_run(call, ctx.obj['targets'])

    if failed_targets:
        if len(ctx.obj['targets']) > 1:
            print('Failed targets:', len(failed_targets))
        ctx.exit(1)
