import asyncio
from samsung_mdc import MDC


async def main(ip, display_id):
    async with MDC(ip, verbose=True) as mdc:
        # First argument of command is always display_id
        status = await mdc.status(display_id)
        print(status)  # Result is always tuple

        if status[0] != MDC.power.POWER_STATE.ON:
            # Command arguments are always Sequence (tuple, list)
            await mdc.power(display_id, [MDC.power.POWER_STATE.ON])
            await mdc.close()  # Force reconnect on next command
            await asyncio.sleep(15)

        await mdc.display_id(display_id, [MDC.display_id.DISPLAY_ID_STATE.ON])
        # You may also use names or values instead of enums
        await mdc.display_id(display_id, ['ON'])  # same
        await mdc.display_id(display_id, [1])     # same


# If you see "Connected" and timeout error, try other display_id (0, 1)
asyncio.run(main('192.168.0.10', 1))
