import pytest
from unittest.mock import Mock
from asyncio import StreamReader, StreamWriter

from samsung_mdc import MDC
from samsung_mdc.connection import (
    HEADER_CODE, RESPONSE_CMD, ACK_CODE, NAK_CODE, get_checksum)


class MDCMock(MDC):
    def __init__(self):
        super().__init__(None)
        self.reader = StreamReader()
        self.writer = Mock(spec=StreamWriter)

    def feed_response(self, command, display_id, data, ack=True):
        # TODO: subcommands not supported
        payload = bytes([
            HEADER_CODE,
            RESPONSE_CMD,
            display_id,
            2 + len(data),
            ACK_CODE if ack else NAK_CODE,
            command.CMD,
        ] + data)
        payload += bytes([get_checksum(payload[1:])])
        self.reader.feed_data(payload)

    def assert_request(self, command, display_id, data):
        # TODO: subcommands not supported
        payload = bytes([
            HEADER_CODE,
            command.CMD,
            display_id,
            len(data),
        ] + data)
        payload += bytes([get_checksum(payload[1:])])
        self.writer.write.assert_called_with(payload)


@pytest.mark.parametrize('command,display_id,req,req_data,resp,resp_data', [
    [MDC.power, 0xFE, [1], [1], [1], [MDC.power.POWER_STATE.ON]],
    [MDC.panel_on_time, 0xFE, [], [], [32768], [128, 0]],
])
@pytest.mark.asyncio
async def test_command(command, display_id, req, req_data, resp, resp_data):
    mdc = MDCMock()
    mdc.feed_response(command, display_id, resp_data)
    result = await getattr(mdc, command.name)(display_id, data=req)
    mdc.assert_request(command, display_id, req_data)
    assert result == tuple(resp)
