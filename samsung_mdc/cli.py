# NOTE: This module is overloading some internals of "click" library
# and may not work stable in case of click major changes in future versions.
# Tested with click==7.1.2

# Beware - if you want something flexible and overridable for cli processing,
# "click" just may be not your best choice...

from enum import Enum
from functools import partial
import asyncio
import os.path

import click

from . import MDCConnection


def _parse_int(x):
    return int(x, 16) if x.startswith('0x') else int(x)


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
        self.fail(f"invalid choice: {value}\n{missing_message}")

    def __repr__(self):
        return f"EnumChoice({self.enum})"


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

    def format_options(self, ctx, formatter):
        # Override this to format ArgumentWithHelp before options
        args = []
        for param in self.get_params(ctx):
            if isinstance(param, click.Argument):
                help = getattr(param, 'help', None)
                args.append((param.metavar or param.name, help or ''))
        if args:
            with formatter.section(self.help_arguments_label):
                formatter.write_dl(args)

        super().format_options(ctx, formatter)


class Group(ArgumentWithHelpCommandMixin, click.Group):
    def get_help_option(self, ctx):
        # Override this to pass parameters to --help
        # This is needed to be able to do "--help COMMAND"
        # without group required arguments
        def show_help(ctx, param, value):
            if value and not ctx.resilient_parsing:
                # Match registered commands and show help for all of them
                from sys import argv
                commands = [
                    ctx.command.commands[name]
                    for name in argv[1:]
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
        return [c.name for c in sorted(
            self.commands.values(),
            key=lambda c: (c.mdc_meta.CMD, getattr(c.mdc_meta, 'SUBCMD', None))
        )]


class MDCCommand(ArgumentWithHelpCommandMixin, click.Command):
    def __init__(self, name, mdc_meta, **kwargs):
        self.mdc_meta = mdc_meta
        name = mdc_meta.name
        kwargs['short_help'] = self._get_params_hint()
        if not mdc_meta.SET:
            kwargs['short_help'] = f'({kwargs["short_help"]})'
        kwargs['help_arguments_label'] = 'Data'
        kwargs['help'] = trim_docstring(mdc_meta.__doc__)

        # Registering params from DATA format
        kwargs.setdefault('params', [])
        for i, field in enumerate(mdc_meta.DATA):
            if issubclass(field.type, Enum):
                type = EnumChoice(field.type)
                help = '|'.join(field.type.__members__.keys())
            else:
                type = field.type
                help = field.type.__name__
                if field.range:
                    help += f' ({field.range.start}-{field.range.stop - 1})'

            kwargs['params'].append(ArgumentWithHelp(
                [f'data_{i}'], metavar=field.name, type=type, help=help))

        super().__init__(name, **kwargs)

    def _get_params_hint(self):
        params = ' '.join([f.name for f in self.mdc_meta.DATA])
        if self.mdc_meta.GET and self.mdc_meta.SET and params:
            params = f'[{params}]'
        return params

    def _get_params_usage(self):
        if self.mdc_meta.SET:
            return self._get_params_hint()
        return ''

    def format_usage(self, ctx, formatter):
        # We need ALL arguments to be OR optional, OR required,
        # so we can't use required on arguments and need to show
        # it properly in usage string
        params = self._get_params_usage()

        # 2. Invoking this on wrong context doesn't show group command
        # required arguments, but we need to invoke this
        # from group context to be able to do "samsung-mdc --help command1"
        params = f' {params}' if params else ''
        formatter.write_usage(
            'samsung-mdc', f'[OPTIONS] TARGET {self.name}{params}')

    def parse_args(self, ctx, args):
        # We need ALL arguments to be OR optional, OR required,
        # so if there is no arguments supplied - this is proper
        # GET command
        if not args and self.mdc_meta.GET:
            ctx.args = args
            return args

        # Avoid "Try 'samsung-mdc {command} --help' for help." message
        # that renders in UsageError,
        # because it's wrong command because of required group command args
        # (maybe this will be fixed in future click versions?)
        try:
            super().parse_args(ctx, args)
        except click.UsageError as exc:
            exc.cmd = None
            raise


class MDCTargetParamType(click.ParamType):
    name = 'mdc_target'

    def get_missing_message(self, param):
        return param.help

    def convert_target(self, value, param, ctx):
        if '@' not in value:
            self.fail(
                f'DISPLAY_ID required '
                '(try 1, for some devices 0xFE(254) means "any")\n'
                f'Format: {param.help}')

        display_id, addr = value.split('@')
        try:
            display_id = _parse_int(display_id)
        except ValueError:
            self.fail(
                f'Invalid DISPLAY_ID "{display_id}" '
                '(int or hex, example: 1, 0x01, 254, 0xFE)\n'
                f'Format: {param.help}')
        if ':' in addr:
            ip, port = addr.split(':')
            try:
                port = int(port)
            except ValueError:
                self.fail(
                    f'Invalid PORT "{port}"\n'
                    f'Format: {param.help}')
        else:
            ip, port = addr, 1515
        return display_id, ip, port

    def convert(self, value, param, ctx):
        if '@' in value:
            return [self.convert_target(value, param, ctx)]
        else:
            if not os.path.exists(value):
                self.fail(
                    f'FILENAME "{value}" does not exist.\n'
                    f'Format: {param.help}')
            else:
                data = open(value).read()
                data = [line.strip() for line in data.split('\n')
                        if line.strip()]
                targets = []
                for i, line in enumerate(data):
                    try:
                        targets.append(self.convert_target(line, param, ctx))
                    except click.UsageError as exc:
                        exc.message = f'{value}:{i}: {exc.message}'
                        raise
                if not targets:
                    self.fail(
                        f'FILENAME "{value} is empty.\n'
                        f'Format: {param.help}')
                return targets


@click.group(
    cls=Group,
    help="Try 'samsung-mdc --help COMMAND' for command info")
@click.argument('target', metavar='TARGET', help=(
        'DISPLAY_ID@IP[:PORT] (default port: 1515) '
        '(example: 1@192.168.0.10:1515) '
        'or FILENAME with target list'
    ), type=MDCTargetParamType(), cls=ArgumentWithHelp)
@click.option('-v', '--verbose', is_flag=True, default=False, type=bool)
@click.pass_context
def cli(ctx, target, verbose):
    ctx.ensure_object(dict)
    ctx.obj['targets'] = target
    ctx.obj['verbose'] = verbose


def register_command(command):
    @click.pass_context
    def _cmd(ctx, **kwargs):
        call_args = tuple(kwargs.values())
        call_args = [call_args] if call_args else []
        targets = [(
            display_id, ip, port, partial(
                command,
                MDCConnection(ip, port, verbose=ctx.obj['verbose']),
                display_id
            )) for display_id, ip, port in ctx.obj['targets']
        ]
        failed_targets = []

        async def print_call(display_id, ip, port, call):
            try:
                print(f'{display_id}@{ip}:{port}', await call(*call_args))
            except Exception as exc:
                failed_targets.append((display_id, ip, port, call))
                print(f'{display_id}@{ip}:{port}',
                      f'{exc.__class__.__name__}: {exc}')
                if ctx.obj['verbose']:
                    raise

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait([
            loop.create_task(print_call(*target))
            for target in targets
        ]))
        loop.close()

        if failed_targets and len(targets) > 1:
            print('Failed targets:', len(failed_targets))
            ctx.exit(1)

    cli.command(cls=MDCCommand, mdc_meta=command.meta)(_cmd)


for command in MDCConnection._commands.values():
    register_command(command)
