from enum import Enum

from . import MDCConnection


def _bit_unmask(val, length=None):
    rv = tuple(reversed(tuple(int(x) for x in tuple('{0:0b}'.format(val)))))
    if length and len(rv) < length:
        return rv + ((0,) * (length - len(rv)))
    return rv


class Field:
    def __init__(self, type, name=None, range=None):
        self.type, self.name, self.range = (
            type, name or type.__name__, range)

    def __call__(self, value):
        return self.type(value)


class _CommandMeta(type):
    def __new__(mcs, name, bases, dict):
        if 'name' not in dict:
            dict['name'] = name.lower()

        if 'DATA' not in dict and bases:
            dict['DATA'] = bases[0].DATA
        dict['DATA'] = [
            x if isinstance(x, Field) else Field(x)
            for x in dict['DATA']
        ]
        cls = type.__new__(mcs, name, bases, dict)
        MDCConnection.register_command(cls)
        return cls


class DAY_PART(Enum):
    AM = 0x01
    PM = 0x00


class SERIAL_NUMBER(metaclass=_CommandMeta):
    CMD = 0x0B
    GET, SET = True, False
    DATA = [Field(str, 'SERIAL_NUM')]


class SOFTWARE_VERSION(metaclass=_CommandMeta):
    CMD = 0x0E
    GET, SET = True, False
    DATA = [Field(str, 'SOFTWARE_VERSION')]


class MODEL_NUMBER(metaclass=_CommandMeta):
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


class POWER(metaclass=_CommandMeta):
    CMD = 0x11
    GET, SET = True, True

    class POWER_STATE(Enum):
        OFF = 0x00
        ON = 0x01
        REBOOT = 0x02

    DATA = [POWER_STATE]


class VOLUME(metaclass=_CommandMeta):
    CMD = 0x12
    GET, SET = True, True
    VOLUME_INT = Field(int, 'VOLUME', range(101))
    DATA = [VOLUME_INT]


class MUTE(metaclass=_CommandMeta):
    CMD = 0x13
    GET, SET = True, True

    class MUTE_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [MUTE_STATE]


class INPUT_SOURCE(metaclass=_CommandMeta):
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


class PICTURE_ASPECT(metaclass=_CommandMeta):
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


class MDC_CONNECTION(metaclass=_CommandMeta):
    CMD = 0x1D
    GET, SET = True, False
    # NOTE: There is no Set command in documentation,
    # but comment states that this parameter is readonly
    # only for RJ45 connection...

    class MDC_CONNECTION_TYPE(Enum):
        RS232C = 0x00
        RJ45 = 0x01

    DATA = [MDC_CONNECTION_TYPE]


class CONTRAST(metaclass=_CommandMeta):
    CMD = 0x24
    GET, SET = True, True
    DATA = [Field(int, 'CONTRAST', range(101))]


class BRIGHTNESS(metaclass=_CommandMeta):
    CMD = 0x25
    GET, SET = True, True
    DATA = [Field(int, 'BRIGHTNESS', range(101))]


class SHARPNESS(metaclass=_CommandMeta):
    CMD = 0x26
    GET, SET = True, True
    DATA = [Field(int, 'SHARPNESS', range(101))]


class COLOR(metaclass=_CommandMeta):
    CMD = 0x27
    GET, SET = True, True
    DATA = [Field(int, 'COLOR', range(101))]


class H_POSITION(metaclass=_CommandMeta):
    CMD = 0x31
    GET, SET = False, True

    class H_POSITION_MOVE_TO(Enum):
        LEFT = 0x00
        RIGHT = 0x01

    DATA = [H_POSITION_MOVE_TO]


class V_POSITION(metaclass=_CommandMeta):
    CMD = 0x32
    GET, SET = False, True

    class V_POSITION_MOVE_TO(Enum):
        UP = 0x00
        DOWN = 0x01

    DATA = [V_POSITION_MOVE_TO]


class AUTO_POWER(metaclass=_CommandMeta):
    CMD = 0x33
    GET, SET = True, True

    class AUTO_POWER_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [AUTO_POWER_STATE]


class CLEAR_MENU(metaclass=_CommandMeta):
    CMD = 0x34
    SUBCMD = 0x00
    GET, SET = False, True

    DATA = []


class IR_LOCK(metaclass=_CommandMeta):
    """
    Enables/disables IR (Infrared) receiving function (Remote Control).

    Working Condition:
    * Can operate regardless of whether power is ON/OFF
    (If DPMS Situation in LFD, it operate Remocon regardless of set value)
    """
    CMD = 0x36
    GET, SET = True, True

    class IR_STATE(Enum):
        DISABLE = 0x00
        ENABLE = 0x01

    DATA = [IR_STATE]


class RGB_CONTRAST(metaclass=_CommandMeta):
    CMD = 0x37
    GET, SET = True, True
    DATA = [Field(int, 'CONTRAST', range(101))]


class RGB_BRIGHTNESS(metaclass=_CommandMeta):
    CMD = 0x38
    GET, SET = True, True
    DATA = [Field(int, 'BRIGHTNESS', range(101))]


class AUTO_ADJUSTMENT_ON(metaclass=_CommandMeta):
    CMD = 0x3D
    SUBCMD = 0x00
    GET, SET = False, True
    DATA = []


class AUTO_LAMP(metaclass=_CommandMeta):
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


class MANUAL_LAMP(metaclass=_CommandMeta):
    """
    Manual Lamp function.

    Note: When Auto Lamp Control is on,
    Manual Lamp Control will automatically turn off.
    """
    CMD = 0x58
    GET, SET = True, True
    DATA = [Field(int, 'LAMP_VALUE', range(101))]


class DEVICE_NAME(metaclass=_CommandMeta):
    """
    It reads the device name which user set up in network.
    Shows the information about entered device name.
    """
    CMD = 0x67
    GET, SET = True, False
    DATA = [Field(str, 'DEVICE_NAME')]


class MODEL_NAME(metaclass=_CommandMeta):
    CMD = 0x8A
    GET, SET = True, False
    DATA = [Field(str, 'MODEL_NAME')]


class OSD(metaclass=_CommandMeta):
    CMD = 0x70
    GET, SET = True, True

    class OSD_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [OSD_STATE]


class OSD_TYPE(metaclass=_CommandMeta):
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
            for i, x in enumerate(_bit_unmask(data[0],
                                  length=len(cls.OSD_TYPE)))
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


class TIMER_15_1(metaclass=_CommandMeta):
    """
    Integrated timer function (15 parameters version).

    Note: This depends on product and will not work on older versions.
    """
    CMD = 0xA4
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

        Field(TIMER_REPEAT, 'REPEAT_ON'),
        # TODO: implement bitmask field
        Field(int, 'MANUAL_WEEKDAY_ON'),

        Field(TIMER_REPEAT, 'REPEAT_OFF'),
        Field(int, 'MANUAL_WEEKDAY_OFF'),

        VOLUME.VOLUME_INT,
        INPUT_SOURCE.INPUT_SOURCE_STATE,
        HOLIDAY_APPLY,
    ]


class TIMER_15_2(TIMER_15_1):
    CMD = 0xA5


class TIMER_15_3(TIMER_15_1):
    CMD = 0xA6


class TIMER_13_1(TIMER_15_1):
    """
    Integrated timer function (13 parameters version).

    Note: This depends on product and will not work on newer versions.
    """
    DATA = [
        f for f in TIMER_15_1.DATA
        if f.name not in ('REPEAT_OFF', 'MANUAL_WEEKDAY_OFF')
    ]


class TIMER_13_2(TIMER_13_1):
    CMD = 0xA5


class TIMER_13_3(TIMER_13_1):
    CMD = 0xA6


class RESET(metaclass=_CommandMeta):
    CMD = 0x9F
    GET, SET = False, True

    class RESET_TARGET(Enum):
        PICTURE = 0x00
        SOUND = 0x01
        SETUP = 0x02  # (System reset)
        ALL = 0x03
        SCREEN_DISPLAY = 0x04

    DATA = [RESET_TARGET]


class VIRTUAL_REMOTE(metaclass=_CommandMeta):
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


class NETWORK_STANDBY(metaclass=_CommandMeta):
    CMD = 0xB5
    GET, SET = True, True

    class NETWORK_STANDBY_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [NETWORK_STANDBY_STATE]


class AUTO_ID_SETTING(metaclass=_CommandMeta):
    CMD = 0xB8
    GET, SET = True, True

    class AUTO_ID_SETTING_STATE(Enum):
        START = 0x00
        END = 0x01

    DATA = [AUTO_ID_SETTING_STATE]


class DISPLAY_ID(metaclass=_CommandMeta):
    CMD = 0xB9
    GET, SET = False, True

    class DISPLAY_ID_STATE(Enum):
        OFF = 0x00
        ON = 0x01

    DATA = [DISPLAY_ID_STATE]


class LAUNCHER_PLAY_VIA(metaclass=_CommandMeta):
    CMD = 0xC7
    SUBCMD = 0x81
    GET, SET = True, True

    class PLAY_VIA_MODE(Enum):
        MAGIC_INFO = 0x00
        URL_LAUNCHER = 0x01
        MAGIC_IWB = 0x02

    DATA = [PLAY_VIA_MODE]


class LAUNCHER_URL_ADDRESS(metaclass=_CommandMeta):
    CMD = 0xC7
    SUBCMD = 0x82
    GET, SET = True, True
    DATA = [Field(str, 'URL_ADDRESS')]


class STATUS(metaclass=_CommandMeta):
    CMD = 0x00
    GET, SET = True, False
    DATA = [
        POWER.POWER_STATE, VOLUME.VOLUME_INT, MUTE.MUTE_STATE,
        INPUT_SOURCE.INPUT_SOURCE_STATE, PICTURE_ASPECT.PICTURE_ASPECT_STATE,
        Field(int, 'N_TIME_NF'), Field(int, 'F_TIME_NF')
    ]
