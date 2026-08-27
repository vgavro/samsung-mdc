import pytest

from samsung_mdc import MDC, commands


_SET_CONTENT_DOWNLOAD_URLS = [
    "http://192.168.1.100:6868/content.json",
    "http://10.0.0.5:8080/content?id=abc123&content_type=ImageContent"
]

_LOW_POWER_WIFI_IP = '192.0.2.123'
_LOW_POWER_WIFI_MAC = '02:00:00:00:00:01'
_LOW_POWER_WIFI_SSID = 'TEST-WIFI'
_LOW_POWER_WIFI_FIRMWARE = 'FRTOS-TEST-FIRMWARE'


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
] + [
    [
        "set_content_download", 0,
        [url],
        bytes([0x80, len(url)]) + url.encode(),
        [url],
        bytes([0x80, len(url)]) + url.encode(),
    ] for url in _SET_CONTENT_DOWNLOAD_URLS
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


@pytest.mark.parametrize('command,cmd,subcmd', [
    ('get_contact_samsung', 0xD2, 0x00),
    ('factory_menu', 0xD2, 0x10),
    ('download_file_cert', 0xD2, 0x20),
    ('network_cert_list', 0xD2, 0x22),
    ('app_cert_list', 0xD2, 0x23),
    ('term_condition', 0xD2, 0x70),
    ('ntp_timezones', 0xD2, 0x71),
    ('low_power_wifi', 0xD2, 0xB0),
])
def test_large_frame_command_metadata(command, cmd, subcmd):
    command = MDC._commands[command]
    assert command.CMD == cmd
    assert command.SUBCMD == subcmd
    assert command.DATA_LENGTH_LARGE is True
    assert command.RESPONSE_LENGTH_LARGE is True


def test_low_power_wifi_response():
    response = (
        bytes([0x00, 0x03, 0x01])
        + bytes([0x80, 0x00, len(_LOW_POWER_WIFI_IP)])
        + _LOW_POWER_WIFI_IP.encode()
        + bytes([0x80, 0x01, len(_LOW_POWER_WIFI_MAC)])
        + _LOW_POWER_WIFI_MAC.encode()
        + bytes([0x80, 0x02, len(_LOW_POWER_WIFI_SSID)])
        + _LOW_POWER_WIFI_SSID.encode()
        + bytes([0x80, 0x09, len(_LOW_POWER_WIFI_FIRMWARE)])
        + _LOW_POWER_WIFI_FIRMWARE.encode()
    )

    assert commands.LOW_POWER_WIFI.parse_response_data(response) == (
        bytes([0x00, 0x03, 0x01]),
        _LOW_POWER_WIFI_IP,
        _LOW_POWER_WIFI_MAC,
        _LOW_POWER_WIFI_SSID,
        _LOW_POWER_WIFI_FIRMWARE,
    )
