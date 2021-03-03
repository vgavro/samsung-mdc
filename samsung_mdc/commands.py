from enum import Enum
from datetime import datetime
from functools import partial, partialmethod

from .exceptions import MDCResponseError, NAKError
from .utils import bit_unmask, parse_mdc_time, pack_mdc_time


class Field:
    def __init__(self, type, name=None, range=None):
        self.type, self.name, self.range = (
            type, name or type.__name__, range)

    def __call__(self, value):
        return self.type(value)


class _CommandMcs(type):
    def __new__(mcs, name, bases, dict):
        if name.startswith('_'):
            return type.__new__(mcs, name, bases, dict)

        if 'name' not in dict:
            dict['name'] = name.lower()

        if 'DATA' not in dict and bases:
            dict['DATA'] = bases[0].DATA
        dict['DATA'] = [
            x if isinstance(x, Field) else Field(x)
            for x in dict['DATA']
        ]
        if '__doc__' not in dict and bases and bases[0].__doc__:
            dict['__doc__'] = bases[0].__doc__

        cls = type.__new__(mcs, name, bases, dict)

        if cls.GET:
            cls.__call__.__defaults__ = (b'',)
        if not cls.SET or not cls.DATA:
            cls.__call__ = partialmethod(cls.__call__, data=b'')

        return cls


class _Command(metaclass=_CommandMcs):
    CMD = None
    SUBCMD = None

    async def __call__(self, connection, display_id, data):
        data = self.parse_response(
            await connection.send(
                (self.CMD, self.SUBCMD)
                if self.SUBCMD is not None else self.CMD, display_id,
                self.pack_payload_data(data) if data else []
            ),
        )
        return self.parse_response_data(data)

    def __get__(self, connection, cls):
        # Allow command to be bounded as instance method
        return partial(self, connection)

    @staticmethod
    def parse_response(response):
        ack, rcmd, data = response
        if not ack:
            raise NAKError(data[0])
        return data

    @classmethod
    def parse_response_data(cls, data, strict_enum=True):
        rv = []
        for i, field in enumerate(cls.DATA):
            if field.type is str:
                rv.append(data[i:].decode('utf8').rstrip('\x00'))
                break
            else:
                try:
                    value = field.type(data[i])
                except ValueError:
                    if not issubclass(field.type, Enum) or strict_enum:
                        raise
                    value = data[i]
                rv.append(value)
        if len(data) != len(rv) and not cls.DATA[-1].type is str:
            raise MDCResponseError('Unexpected data length', data)
        return tuple(rv)

    @classmethod
    def pack_payload_data(cls, data):
        rv = bytes()
        for i, field in enumerate(cls.DATA):
            if field.type is str:
                rv += data[i].encode()
            else:
                rv += bytes((getattr(data[i], 'value', data[i]),))
        if len(data) != len(rv) and not cls.DATA[-1].type is str:
            raise ValueError('Unexpected data length')
        return rv

    @classmethod
    def get_order(cls):
        return (cls.CMD, cls.SUBCMD)


class DAY_PART(Enum):
    PM = 0x00
    AM = 0x01


class LOCK_STATE(Enum):
    OFF = 0x00
    ON = 0x01


class SERIAL_NUMBER(_Command):
    CMD = 0x0B
    GET, SET = True, False
    DATA = [Field(str, 'SERIAL_NUMBER')]


class SOFTWARE_VERSION(_Command):
    CMD = 0x0E
    GET, SET = True, False
    DATA = [Field(str, 'SOFTWARE_VERSION')]


class MODEL_NUMBER(_Command):
    CMD = 0x10
    GET, SET = True, False

    class MODEL_SPECIES(Enum):
        PDP = 0x01
        LCD = 0x02
        DLP = 0x03
        LED = 0x04
        CRT = 0x05
        OLED = 0x06

    class TV_SUPPORT(Enum):
        SUPPORTED = 0x00
        NOT_SUPPORTED = 0x01

    # NOTE: Actually there is list of MODEL_NUMBER codes in specification,
    # but it's TOO long
    DATA = [MODEL_SPECIES, Field(int, 'MODEL_NUMBER'), TV_SUPPORT]


class POWER(_Command):
    CMD = 0x11
    GET, SET = True, True

    class POWER_STATE(Enum):
        OFF = 0x00
        ON = 0x01
        REBOOT = 0x02

    DATA = [POWER_STATE]


class VOLUME(_Command):
    CMD = 0x12
    GET, SET = True, True
    VOLUME_INT = Field(int, 'VOLUME', range(101))
    DATA = [VOLUME_INT]


class MUTE(_Command):
    CMD = 0x13
    GET, SET = True, True

    class MUTE_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [MUTE_STATE]


class INPUT_SOURCE(_Command):
    CMD = 0x14
    GET, SET = True, True

    class INPUT_SOURCE_STATE(Enum):
        S_VIDEO = 0x04
        COMPONENT = 0x08
        AV = 0x0C
        AV2 = 0x0D
        SCART1 = 0x0E
        DVI = 0x18
        PC = 0x14
        BNC = 0x1E
        DVI_VIDEO = 0x1F
        MAGIC_INFO = 0x20
        HDMI1 = 0x21
        HDMI1_PC = 0x22
        HDMI2 = 0x23
        HDMI2_PC = 0x24
        DISPLAY_PORT_1 = 0x25
        DISPLAY_PORT_2 = 0x26
        DISPLAY_PORT_3 = 0x27
        RF_TV = 0x30
        HDMI3 = 0x31
        HDMI3_PC = 0x32
        HDMI4 = 0x33
        HDMI4_PC = 0x34
        TV_DTV = 0x40
        PLUG_IN_MODE = 0x50
        HD_BASE_T = 0x55
        MEDIA_MAGIC_INFO_S = 0x60
        WIDI_SCREEN_MIRRORING = 0x61
        INTERNAL_USB = 0x62
        URL_LAUNCHER = 0x63
        IWB = 0x64

    DATA = [INPUT_SOURCE_STATE]


class PICTURE_ASPECT(_Command):
    CMD = 0x15
    GET, SET = True, True

    class PICTURE_ASPECT_STATE(Enum):
        PC_16_9 = 0x10
        PC_4_3 = 0x18
        PC_ORIGINAL_RATIO = 0x20
        PC_21_9 = 0x21

        VIDEO_AUTO_WIDE = 0x00
        VIDEO_16_9 = 0x01
        VIDEO_ZOOM = 0x04
        VIDEO_ZOOM_1 = 0x05
        VIDEO_ZOOM_2 = 0x06
        VIDEO_SCREEN_FIT = 0x09
        VIDEO_4_3 = 0x0B
        VIDEO_WIDE_FIT = 0x0C
        VIDEO_CUSTOM = 0x0D
        VIDEO_SMART_VIEW_1 = 0x0E
        VIDEO_SMART_VIEW_2 = 0x0F
        VIDEO_WIDE_ZOOM = 0x31
        VIDEO_21_9 = 0x32

    DATA = [PICTURE_ASPECT_STATE]


class MDC_CONNECTION(_Command):
    CMD = 0x1D
    GET, SET = True, False
    # NOTE: There is no Set command in documentation,
    # but comment states that this parameter is readonly
    # only for RJ45 connection...

    class MDC_CONNECTION_TYPE(Enum):
        RS232C = 0x00
        RJ45 = 0x01

    DATA = [MDC_CONNECTION_TYPE]


class CONTRAST(_Command):
    CMD = 0x24
    GET, SET = True, True
    DATA = [Field(int, 'CONTRAST', range(101))]


class BRIGHTNESS(_Command):
    CMD = 0x25
    GET, SET = True, True
    DATA = [Field(int, 'BRIGHTNESS', range(101))]


class SHARPNESS(_Command):
    CMD = 0x26
    GET, SET = True, True
    DATA = [Field(int, 'SHARPNESS', range(101))]


class COLOR(_Command):
    CMD = 0x27
    GET, SET = True, True
    DATA = [Field(int, 'COLOR', range(101))]


class H_POSITION(_Command):
    CMD = 0x31
    GET, SET = False, True

    class H_POSITION_MOVE_TO(Enum):
        LEFT = 0x00
        RIGHT = 0x01

    DATA = [H_POSITION_MOVE_TO]


class V_POSITION(_Command):
    CMD = 0x32
    GET, SET = False, True

    class V_POSITION_MOVE_TO(Enum):
        UP = 0x00
        DOWN = 0x01

    DATA = [V_POSITION_MOVE_TO]


class AUTO_POWER(_Command):
    CMD = 0x33
    GET, SET = True, True

    class AUTO_POWER_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [AUTO_POWER_STATE]


class CLEAR_MENU(_Command):
    CMD = 0x34
    SUBCMD = 0x00
    GET, SET = False, True

    DATA = []


class IR_LOCK(_Command):
    """
    Enables/disables IR (Infrared) receiving function (Remote Control).

    Working Condition:
    * Can operate regardless of whether power is ON/OFF.
    (If DPMS Situation in LFD, it operate Remocon regardless of set value).
    """
    CMD = 0x36
    GET, SET = True, True

    class IR_STATE(Enum):
        DISABLED = 0x00
        ENABLED = 0x01

    DATA = [IR_STATE]


class RGB_CONTRAST(_Command):
    CMD = 0x37
    GET, SET = True, True
    DATA = [Field(int, 'CONTRAST', range(101))]


class RGB_BRIGHTNESS(_Command):
    CMD = 0x38
    GET, SET = True, True
    DATA = [Field(int, 'BRIGHTNESS', range(101))]


class AUTO_ADJUSTMENT_ON(_Command):
    CMD = 0x3D
    SUBCMD = 0x00
    GET, SET = False, True
    DATA = []


class AUTO_LAMP(_Command):
    """
    Auto Lamp function.

    Note: When Manual Lamp Control is on,
    Auto Lamp Control will automatically turn off.
    """
    CMD = 0x57
    GET, SET = True, True

    DATA = [
        Field(int, 'AUTO_LAMP_MAX_HOUR', range(1, 13)),
        Field(int, 'AUTO_LAMP_MAX_MINUTE', range(60)),
        Field(DAY_PART, 'AUTO_LAMP_MAX_DAY_PART'),
        Field(int, 'AUTO_LAMP_MAX_VALUE', range(101)),

        Field(int, 'AUTO_LAMP_MIN_HOUR', range(1, 13)),
        Field(int, 'AUTO_LAMP_MIN_MINUTE', range(60)),
        Field(DAY_PART, 'AUTO_LAMP_MIN_DAY_PART'),
        Field(int, 'AUTO_LAMP_MIN_VALUE', range(101)),
    ]


class MANUAL_LAMP(_Command):
    """
    Manual Lamp function.

    Note: When Auto Lamp Control is on,
    Manual Lamp Control will automatically turn off.
    """
    CMD = 0x58
    GET, SET = True, True
    DATA = [Field(int, 'LAMP_VALUE', range(101))]


class INVERSE(_Command):
    CMD = 0x5A
    GET, SET = True, True

    class INVERSE_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [INVERSE_STATE]


class SAFETY_LOCK(_Command):
    CMD = 0x5D
    GET, SET = True, True
    DATA = [LOCK_STATE]


class PANEL_LOCK(_Command):
    CMD = 0x5F
    GET, SET = True, True
    DATA = [LOCK_STATE]


class DEVICE_NAME(_Command):
    """
    It reads the device name which user set up in network.
    Shows the information about entered device name.
    """
    CMD = 0x67
    GET, SET = True, False
    DATA = [Field(str, 'DEVICE_NAME')]


class OSD(_Command):
    CMD = 0x70
    GET, SET = True, True

    class OSD_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [OSD_STATE]


class ALL_KEYS_LOCK(_Command):
    """
    Turns both REMOCON and Panel Key Lock function on/off.

    Note: Can operate regardless of whether power is on/off.
    """

    # TODO: REMOCON? Remote Control?
    CMD = 0x77
    GET, SET = True, True

    class LOCK_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [LOCK_STATE]


class MODEL_NAME(_Command):
    CMD = 0x8A
    GET, SET = True, False
    DATA = [Field(str, 'MODEL_NAME')]


class OSD_TYPE(_Command):
    CMD = 0xA3
    GET, SET = True, True

    class OSD_TYPE(Enum):
        SOURCE = 0x00
        NOT_OPTIMUM_MODE = 0x01
        NO_SIGNAL = 0x02
        MDC = 0x03
        SCHEDULE_CHANNEL = 0x04

    DATA = [OSD_TYPE, OSD.OSD_STATE]

    @classmethod
    def parse_response_data(cls, data):
        return tuple(
            (cls.OSD_TYPE(i), OSD.OSD_STATE(x))
            for i, x in enumerate(
                bit_unmask(data[0], length=len(cls.OSD_TYPE)))
        )


class TIMER_REPEAT(Enum):
    ONCE = 0x00
    EVERYDAY = 0x01
    MON_FRI = 0x02
    MON_SAT = 0x03
    SAT_SUN = 0x04
    MANUAL_WEEKDAY = 0x05


class HOLIDAY_APPLY(Enum):
    DONT_APPLY_BOTH = 0x00
    APPLY_BOTH = 0x01
    ON_TIMER_ONLY_APPLY = 0x02
    OFF_TIMER_ONLY_APPLY = 0x03


class TIMER_15(_Command):
    """
    Integrated timer function (15 parameters version).

    Note: This depends on product and will not work on older versions.
    """
    CMD = Field(int, 'TIMER_ID', range(1, 8))
    _TIMER_ID_CMD = [0xA4, 0xA5, 0xA6, 0xAB, 0xAC, 0xAD, 0xAE]
    GET, SET = True, True

    DATA = [
        Field(int, 'ON_HOUR', range(1, 13)),
        Field(int, 'ON_MINUTE', range(60)),
        Field(DAY_PART, 'ON_DAY_PART'),
        Field(bool, 'ON_ACT'),

        Field(int, 'OFF_HOUR', range(1, 13)),
        Field(int, 'OFF_MINUTE', range(60)),
        Field(DAY_PART, 'OFF_DAY_PART'),
        Field(bool, 'OFF_ACT'),

        Field(TIMER_REPEAT, 'ON_REPEAT'),
        # TODO: implement bitmask field
        Field(int, 'ON_MANUAL_WEEKDAY'),

        Field(TIMER_REPEAT, 'OFF_REPEAT'),
        Field(int, 'OFF_MANUAL_WEEKDAY'),

        VOLUME.VOLUME_INT,
        INPUT_SOURCE.INPUT_SOURCE_STATE,
        HOLIDAY_APPLY,
    ]

    async def __call__(self, connection, display_id, timer_id, data):
        cmd = self._TIMER_ID_CMD[timer_id - 1]
        data = self.parse_response(
            await connection.send(
                cmd, display_id,
                self.pack_payload_data(data) if data else []
            ),
        )
        return self.parse_response_data(data)

    @classmethod
    def get_order(cls):
        return (0xA4, cls.name)


class TIMER_13(TIMER_15):
    """
    Integrated timer function (13 parameters version).

    Note: This depends on product and will not work on newer versions.
    """
    DATA = []
    for f in TIMER_15.DATA:
        if f.name not in ('OFF_REPEAT', 'OFF_MANUAL_WEEKDAY'):
            if f.name in ('ON_REPEAT', 'ON_MANUAL_WEEKDAY'):
                DATA.append(Field(f.type, f.name.replace('ON_', ''), f.range))
            else:
                DATA.append(f)


class RESET(_Command):
    CMD = 0x9F
    GET, SET = False, True

    class RESET_TARGET(Enum):
        PICTURE = 0x00
        SOUND = 0x01
        SETUP = 0x02  # (System reset)
        ALL = 0x03
        SCREEN_DISPLAY = 0x04

    DATA = [RESET_TARGET]


class CLOCK_S(_Command):
    """
    Current time function (second precision).

    Note: This is for models developed after 2013.
    For older models see CLOCK_M function (minute precision).
    """
    GET, SET = True, True
    CMD = 0xC5

    DATA = [Field(datetime, 'DATETIME')]

    @classmethod
    def parse_response_data(cls, data):
        if not len(data) == 8:
            raise MDCResponseError('Unexpected data length', data)
        time = parse_mdc_time(data[7], data[1], data[2], data[3])
        return (datetime(
            int.from_bytes(data[5:7], 'big'),  # year
            data[4], data[0],  # month, day
            time.hour, time.minute, time.second
        ),)

    @classmethod
    def pack_payload_data(cls, data, seconds=True):
        print(data)
        if len(data) != 1:
            raise ValueError('Unexpected data length')
        dt = data[0]
        day_part, hour, minute, second = pack_mdc_time(dt.time())
        return (
            bytes([dt.day, hour, minute])
            + (seconds and bytes([second]) or b'')
            + bytes([dt.month])
            + int.to_bytes(dt.year, 2, 'big') + bytes([day_part]))


class CLOCK_M(CLOCK_S):
    """
    Current time function (minute precision).

    Note: This is for models developed until 2013.
    For newer models see CLOCK_S function (seconds precision).
    """
    CMD = 0xA7

    @classmethod
    def parse_response_data(cls, data):
        if not len(data) == 7:
            raise MDCResponseError('Unexpected data length', data)
        time = parse_mdc_time(data[6], data[1], data[2])
        return (datetime(
            int.from_bytes(data[4:6], 'big'),  # year
            data[3], data[0],  # month, day
            time.hour, time.minute, time.second
        ),)

    @classmethod
    def pack_payload_data(cls, data):
        return CLOCK_S.pack_payload_data(data, seconds=False)


class VIRTUAL_REMOTE(_Command):
    """
    This function support that MDC command can work same as remote control.

    Note: In a certain model, 0x79 content key works as Home
    and 0x1f Display key works as Info.
    """
    CMD = 0xB0
    GET, SET = False, True

    class REMOTE_KEY_CODE(Enum):
        KEY_SOURCE = 0x01
        KEY_POWER = 0x02
        KEY_1 = 0x04
        KEY_2 = 0x05
        KEY_3 = 0x06
        KEY_VOLUME_UP = 0x07
        KEY_4 = 0x08
        KEY_5 = 0x09
        KEY_6 = 0x0A
        KEY_VOLUME_DOWN = 0x0B
        KEY_7 = 0x0C
        KEY_8 = 0x0D
        KEY_9 = 0x0E
        KEY_MUTE = 0x0F
        KEY_CHANNEL_DOWN = 0x10
        KEY_0 = 0x11
        KEY_CHANNEL_UP = 0x12
        KEY_GREEN = 0x14
        KEY_YELLOW = 0x15
        KEY_CYAN = 0x16
        KEY_MENU = 0x1A
        KEY_DISPLAY = 0x1F
        KEY_DIGIT = 0x23
        KEY_PIP_TV_VIDEO = 0x24
        KEY_EXIT = 0x2D
        KEY_REW = 0x45
        KEY_STOP = 0x46
        KEY_PLAY = 0x47
        KEY_FF = 0x48
        KEY_PAUSE = 0x4A
        KEY_TOOLS = 0x4B
        KEY_RETURN = 0x58
        KEY_MAGICINFO_LITE = 0x5B
        KEY_CURSOR_UP = 0x60
        KEY_CURSOR_DOWN = 0x61
        KEY_CURSOR_RIGHT = 0x62
        KEY_CURSOR_LEFT = 0x65
        KEY_ENTER = 0x68
        KEY_RED = 0x6C
        KEY_LOCK = 0x77
        KEY_CONTENT = 0x79
        DISCRET_POWER_OFF = 0x98
        KEY_3D = 0x9F

    DATA = [REMOTE_KEY_CODE]


class NETWORK_STANDBY(_Command):
    CMD = 0xB5
    GET, SET = True, True

    class NETWORK_STANDBY_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [NETWORK_STANDBY_STATE]


class AUTO_ID_SETTING(_Command):
    CMD = 0xB8
    GET, SET = True, True

    class AUTO_ID_SETTING_STATE(Enum):
        START = 0x00
        END = 0x01

    DATA = [AUTO_ID_SETTING_STATE]


class DISPLAY_ID(_Command):
    CMD = 0xB9
    GET, SET = False, True

    class DISPLAY_ID_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [DISPLAY_ID_STATE]


class LAUNCHER_PLAY_VIA(_Command):
    CMD = 0xC7
    SUBCMD = 0x81
    GET, SET = True, True

    class PLAY_VIA_MODE(Enum):
        MAGIC_INFO = 0x00
        URL_LAUNCHER = 0x01
        MAGIC_IWB = 0x02

    DATA = [PLAY_VIA_MODE]


class LAUNCHER_URL_ADDRESS(_Command):
    CMD = 0xC7
    SUBCMD = 0x82
    GET, SET = True, True
    DATA = [Field(str, 'URL_ADDRESS')]


class STATUS(_Command):
    CMD = 0x00
    GET, SET = True, False
    DATA = [
        POWER.POWER_STATE, VOLUME.VOLUME_INT, MUTE.MUTE_STATE,
        INPUT_SOURCE.INPUT_SOURCE_STATE, PICTURE_ASPECT.PICTURE_ASPECT_STATE,
        Field(int, 'N_TIME_NF'), Field(int, 'F_TIME_NF')
    ]
