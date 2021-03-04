#!./venv/bin/python

import click

from samsung_mdc.cli import cli


def get_usage_docs():
    with click.Context(cli, info_name='samsung-mdc') as ctx:
        group_help, commands = cli.get_help(ctx).split('\nCommands:\n')
        rv = '```\n' + group_help + '\n```\n### Commands:\n\n'

        for name in cli.list_commands(ctx):
            command = cli.commands[name]
            if hasattr(command, '_get_params_hint'):
                hint = command._get_params_hint().strip()
            else:
                hint = ' '.join(command.collect_usage_pieces(ctx)).strip()
            if hasattr(command, 'mdc_command'):
                if not command.mdc_command.SET:
                    hint = f'({hint})'

            hint = hint and f'`{hint}`' or ''
            rv += f'* [{name}](#{name}) {hint}\n'

        for name in cli.list_commands(ctx):
            rv += f'\n#### {name}\n```\n' + (
                cli.commands[name].get_help(ctx)
                .replace('\n\nOptions:\n  --help  Show this message and exit.',
                         '')
            ) + '\n```'
        return rv


def create_readme():
    with open('README.md', 'w') as fh:
        fh.write(
            open('.readme/README.template.md').read()
            .replace('{{usage}}', get_usage_docs())
            .replace('{{command_count}}', str(len(cli.commands)))
        )


if __name__ == '__main__':
    create_readme()
