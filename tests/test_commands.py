import pytest

from samsung_mdc import MDC


@pytest.mark.parametrize('command,display_id,req,req_data,resp,resp_data', [
    [
        'power', 0,
        [1], [1],
        [1], [MDC.power.POWER_STATE.ON]
    ],
    [
        'panel_on_time', 0,
        [], [],
        [2 ** 15], [128, 0]
    ],
    [
        'panel_on_time', 0,
        [], [],
        [2 ** 15], [0, 128, 0]  # dynamic response length for newer models
    ],
    [
        'panel_on_time', 0,
        [], [],
        [2 ** 16 + 1], [1, 0, 1]
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
    mdc_mock.feed_response(command, display_id, resp_data)
    result = await getattr(mdc_mock, command.name)(display_id, data=req)
    mdc_mock.assert_request(command, display_id, req_data)
    assert result == tuple(resp)
