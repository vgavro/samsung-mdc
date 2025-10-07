import pytest

from samsung_mdc import MDC, commands


@pytest.mark.parametrize('command,display_id,req,req_data,resp,resp_data', [
    [
        'power', 0,
        [1], [1],
        [1], [commands.POWER.POWER_STATE.ON]
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
    [
        'set_content_download', 0,
        ['http://192.168.1.100:6868/content.json'],
        b'http://192.168.1.100:6868/content.json',
        ['http://192.168.1.100:6868/content.json'],
        b'http://192.168.1.100:6868/content.json',
    ],
    [
        'set_content_download', 0,
        ['http://10.0.0.5:8080/content?id=abc123&content_type=ImageContent'],
        b'http://10.0.0.5:8080/content?id=abc123&content_type=ImageContent',
        ['http://10.0.0.5:8080/content?id=abc123&content_type=ImageContent'],
        b'http://10.0.0.5:8080/content?id=abc123&content_type=ImageContent',
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
