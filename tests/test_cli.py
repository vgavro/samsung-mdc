import re

import pytest
import nest_asyncio  # type: ignore[import-not-found]
from click.testing import CliRunner
from samsung_mdc.cli import cli
from samsung_mdc import MDC


def run(*args):
    nest_asyncio.apply()
    return CliRunner().invoke(cli, args, prog_name='samsung-mdc')


def test_help():
    # running without arguments returns exit code 2 (usage error)
    # since click>=8.2.0 https://github.com/pallets/click/pull/1489
    for rv, expect_exit_codes in [(run("--help"), (0,)), (run(), (0, 2))]:
        assert rv.exit_code in expect_exit_codes, rv.output
        assert re.search("^Usage:", rv.output, re.MULTILINE)
        assert re.search("^Options:", rv.output, re.MULTILINE)
        assert re.search("^Commands:", rv.output, re.MULTILINE)



@pytest.mark.parametrize('command,display_id,req,req_data,resp,resp_data', [
    [
        'power', 0,
        ['1'], [1],
        ['<POWER_STATE.ON:1>'], [1]
    ],
    [
        'panel_on_time', 0,
        [], [],
        [32768], [128, 0]
    ],
    [
        'network_ap_config', 0,
        ['ssid', 'passwd'], bytes([0, 4]) + b'ssid' + bytes([1, 6]) + b'passwd',
        ['ssid', 'passwd'], bytes([0, 4]) + b'ssid' + bytes([1, 6]) + b'passwd',
    ],
])
@pytest.mark.asyncio
async def test_command(
    mdc_mock, command, display_id, req, req_data, resp, resp_data
):
    command = MDC._commands[command]
    target = f'{display_id}@127.0.0.1'
    mdc_mock.feed_response(command, display_id, resp_data)
    rv = run(target, command.name, *map(str, req))
    mdc_mock.assert_request(command, display_id, req_data)
    assert rv.exit_code == 0, rv.output
    assert rv.output == f'{target} {" ".join(map(str, resp))}\n'
