from typing import TYPE_CHECKING

from .command import Command
from .fields import (
    Enum as EnumField, Int, Bool, Str, StrCoded,
    Time12H, Time, DateTime, Bitmask, IPAddress, VideoWallModel)


if TYPE_CHECKING:
    from enum import IntEnum
else:
    try:
        from enum import IntEnum
    except ImportError:
        from enum import Enum

        class IntEnum(int, Enum):
            ...


class _COMMON:
    # It's better to re-use enumerations from "main" related commands,
    # like INPUT_SOURCE.INPUT_SOURCE_STATE / PICTURE_ASPECT.PICTURE_ASPECT_STATE
    # Use _COMMON namespace if there is no obvious "main" command,
    # avoid using it for too simple definitions.

    class ORIENTATION_MODE_STATE(IntEnum):
        LANDSCAPE_0 = 0x00
        PORTRAIT_270 = 0x01
        LANDSCAPE_180 = 0x02
        PORTRAIT_90 = 0x03


class SERIAL_NUMBER(Command):
    CMD = 0x0B
    GET, SET = True, False
    DATA = [Str('SERIAL_NUMBER')]


class ERROR_STATUS(Command):
    CMD = 0x0D
    GET, SET = True, False

    class LAMP_ERROR_STATE(IntEnum):
        NORMAL = 0x00
        ERROR = 0x01

    class TEMPERATURE_ERROR_STATE(IntEnum):
        NORMAL = 0x00
        ERROR = 0x01

    class BRIGHTNESS_SENSOR_ERROR_STATE(IntEnum):
        NONE = 0x00
        ERROR = 0x01
        NORMAL = 0x02

    class INPUT_SOURCE_ERROR_STATE(IntEnum):
        """
        No_Sync Error
        Note: Invalid status will be replied with app source selected state.
        Error status will be replied with input signal of not supported
        resolution or no signal.
        """
        NORMAL = 0x00
        ERROR = 0x01
        INVALID = 0x02

    class FAN_ERROR_STATE(IntEnum):
        NORMAL = 0x00
        ERROR = 0x01
        NONE = 0x02  # Fan is not supported

    DATA = [
        LAMP_ERROR_STATE,
        TEMPERATURE_ERROR_STATE,
        BRIGHTNESS_SENSOR_ERROR_STATE,
        INPUT_SOURCE_ERROR_STATE,
        Int('TEMPERATURE'),
        FAN_ERROR_STATE,
    ]


class SOFTWARE_VERSION(Command):
    CMD = 0x0E
    GET, SET = True, False
    DATA = [Str('SOFTWARE_VERSION')]


class MODEL_NUMBER(Command):
    CMD = 0x10
    GET, SET = True, False

    class MODEL_SPECIES(IntEnum):
        PDP = 0x01
        LCD = 0x02
        DLP = 0x03
        LED = 0x04
        CRT = 0x05
        OLED = 0x06

    class TV_SUPPORT(IntEnum):
        SUPPORTED = 0x00
        NOT_SUPPORTED = 0x01

    # NOTE: Actually there is list of MODEL_CODE in specification,
    # but it's TOO long, and it's TOO old (newer models gets new code),
    # so better use MODEL_NAME for this case
    DATA = [MODEL_SPECIES, Int('MODEL_CODE'), TV_SUPPORT]


class POWER(Command):
    CMD = 0x11
    GET, SET = True, True

    class POWER_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01
        REBOOT = 0x02

    DATA = [POWER_STATE]


class VOLUME(Command):
    CMD = 0x12
    GET, SET = True, True
    VOLUME = Int('VOLUME', range(101))
    DATA = [VOLUME]


class MUTE(Command):
    CMD = 0x13
    GET, SET = True, True

    class MUTE_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01
        NONE = 0xFF  # Unavailable

    DATA = [MUTE_STATE]


class INPUT_SOURCE(Command):
    """
    Get/Set the device source which is shown on the screen.

    DVI_VIDEO, HDMI1_PC, HDMI2_PC, HDMI3_PC, HDMI4_PC: get only.

    URL_LAUNCHER, MAGIC_INFO, TV or some ports require support by model.

    On TIMER functions, Do not use WIDI_SCREEN_MIRRORING.
    """

    CMD = 0x14
    GET, SET = True, True

    class INPUT_SOURCE_STATE(IntEnum):
        # not a valid value for INPUT_SOURCE, but valid for auto_source
        NONE = 0x00

        S_VIDEO = 0x04
        COMPONENT = 0x08
        AV = 0x0C
        AV2 = 0x0D
        SCART1 = 0x0E
        DVI = 0x18
        PC = 0x14
        BNC = 0x1E
        DVI_VIDEO = 0x1F  # get only
        MAGIC_INFO = 0x20
        HDMI1 = 0x21
        HDMI1_PC = 0x22  # get only
        HDMI2 = 0x23
        HDMI2_PC = 0x24  # get only
        DISPLAY_PORT_1 = 0x25
        DISPLAY_PORT_2 = 0x26
        DISPLAY_PORT_3 = 0x27
        RF_TV = 0x30  # deprecated
        HDMI3 = 0x31
        HDMI3_PC = 0x32  # get only
        HDMI4 = 0x33
        HDMI4_PC = 0x34  # get only
        TV_DTV = 0x40
        PLUG_IN_MODE = 0x50
        HD_BASE_T = 0x55
        OCM = 0x56
        MEDIA_MAGIC_INFO_S = 0x60
        WIDI_SCREEN_MIRRORING = 0x61
        INTERNAL_USB = 0x62
        URL_LAUNCHER = 0x63
        IWB = 0x64
        WEB_BROWSER = 0x65
        REMOTE_WORKSPACE = 0x66

    DATA = [INPUT_SOURCE_STATE]


class PICTURE_ASPECT(Command):
    """
    Get/Set the device picture size (aspect ratio).

    Working Condition:
    Will not work with VIDEO_WALL_STATE is ON.

    Note:
    Some of the image sizes are not supported depending on input signals.
    """
    CMD = 0x15
    GET, SET = True, True

    class PICTURE_ASPECT_STATE(IntEnum):
        PC_16_9 = 0x10
        PC_4_3 = 0x18
        PC_ORIGINAL_RATIO = 0x20
        PC_21_9 = 0x21
        PC_CUSTOM = 0x22

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


class SCREEN_MODE(Command):
    CMD = 0x18
    GET, SET = True, True

    class SCREEN_MODE_STATE(IntEnum):
        MODE_16_9 = 0x01
        MODE_ZOOM = 0x04
        MODE_4_3 = 0x0B
        MODE_WIDE_ZOOM = 0x31

    DATA = [SCREEN_MODE_STATE]


class SCREEN_SIZE(Command):
    CMD = 0x19
    GET, SET = True, False

    DATA = [Int('INCHES', range(256))]


class NETWORK_CONFIGURATION(Command):
    CMD = 0x1B
    SUBCMD = 0x82
    GET, SET = True, True

    DATA = [
        IPAddress('IP_ADDRESS'),
        IPAddress('SUBNET_MASK'),
        IPAddress('GATEWAY_ADDRESS'),
        IPAddress('DNS_SERVER_ADDRESS'),
    ]


class NETWORK_MODE(Command):
    CMD = 0x1B
    SUBCMD = 0x85
    GET, SET = True, True

    class NETWORK_MODE_STATE(IntEnum):
        DYNAMIC = 0x00
        STATIC = 0x01

    DATA = [NETWORK_MODE_STATE]


class WEEKLY_RESTART(Command):
    CMD = 0x1B
    SUBCMD = 0xA2
    GET, SET = True, True

    class WEEKDAY(IntEnum):
        # NOTE: codes differs from TIMER_15.WEEKDAY
        SUN = 0x00
        SAT = 0x01
        FRI = 0x02
        THU = 0x03
        WED = 0x04
        TUE = 0x05
        MON = 0x06

    DATA = [Bitmask(WEEKDAY), Time()]


class NETWORK_AP_CONFIG(Command):
    """
    Add new SSID info to device connection history with its password.

    Note: device may change network and response may not be received.
    """
    CMD = 0x1B
    SUBCMD = 0x8A
    GET, SET = False, True

    DATA = [StrCoded(0x00, 'SSID'), StrCoded(0x01, 'PASSWORD')]


class MAGICINFO_CHANNEL(Command):
    """
    Set MagicInfo Channel by Direct Channel Number
    which is used by MagicInfo S Player.
    """
    CMD = 0x1C
    SUBCMD = 0x81
    GET, SET = False, True

    DATA = [Int('CHANNEL_NUMBER', length=2, byteorder='big')]


class MAGICINFO_SERVER(Command):
    """
    MagicInfo Server URL.

    Example: "http://example.com:80"
    """
    CMD = 0x1C
    SUBCMD = 0x82
    GET, SET = True, True

    DATA = [Str('MAGICINFO_SERVER_URL')]


class MAGICINFO_CONTENT_ORIENTATION(Command):
    CMD = 0x1C
    SUBCMD = 0x83
    GET, SET = True, True

    DATA = [_COMMON.ORIENTATION_MODE_STATE]


class SET_CONTENT_DOWNLOAD(Command):
    """
    Control the device URL of content download.
    The device will download content (images, schedules) from the specified URL.

    Working Condition:
    - Depends on each model spec it will be supported or not.
    - Supports ePaper displays (e.g., EM32DX) and Smart Signage displays.
    - Device must have network connectivity to the content server.

    CONTENT_URL: ASCII code data for the content server address.
    The URL should point to a content server that provides:
    - Content manifest (content.json) with schedule and media references
    - Media files (images) accessible via URLs in the manifest

    Example: "http://192.168.1.100:6868/content.json"

    Note: This command is used for mobile-to-display content transfer and
    automated content management for digital signage.
    """
    CMD = 0xC7
    SUBCMD = 0x53
    GET, SET = False, True

    DATA = [StrCoded(0x80, 'CONTENT_URL')]


class MDC_CONNECTION(Command):
    """
    Note: Depends on the product specification,
    if it is set as RJ45 then serial MDC will not work.
    """
    CMD = 0x1D
    GET, SET = True, True

    class MDC_CONNECTION_TYPE(IntEnum):
        RS232C = 0x00
        RJ45 = 0x01

    DATA = [MDC_CONNECTION_TYPE]


class CONTRAST(Command):
    CMD = 0x24
    GET, SET = True, True
    DATA = [Int('CONTRAST', range(101))]


class BRIGHTNESS(Command):
    CMD = 0x25
    GET, SET = True, True
    DATA = [Int('BRIGHTNESS', range(101))]


class SHARPNESS(Command):
    CMD = 0x26
    GET, SET = True, True
    DATA = [Int('SHARPNESS', range(101))]


class COLOR(Command):
    CMD = 0x27
    GET, SET = True, True
    DATA = [Int('COLOR', range(101))]


class TINT(Command):
    """
    Control the device tint. Adjust the ratio of green to red tint level.

    Red: TINT value, Green: ( 100 - TINT ) value.

    Note: Tint could only be set in 50 Steps (0, 2, 4, 6... 100).
    """
    CMD = 0x28
    GET, SET = True, True
    DATA = [Int('TINT', range(101))]


class H_POSITION(Command):
    CMD = 0x31
    GET, SET = False, True

    class H_POSITION_MOVE_TO(IntEnum):
        LEFT = 0x00
        RIGHT = 0x01

    DATA = [H_POSITION_MOVE_TO]


class V_POSITION(Command):
    CMD = 0x32
    GET, SET = False, True

    class V_POSITION_MOVE_TO(IntEnum):
        UP = 0x00
        DOWN = 0x01

    DATA = [V_POSITION_MOVE_TO]


class AUTO_POWER(Command):
    CMD = 0x33
    GET, SET = True, True

    class AUTO_POWER_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [AUTO_POWER_STATE]


class CLEAR_MENU(Command):
    CMD = 0x34
    SUBCMD = 0x00
    GET, SET = False, True

    DATA = []


class IR_STATE(Command):
    """
    Enables/disables IR (Infrared) receiving function (Remote Control).

    Working Condition:
    * Can operate regardless of whether power is ON/OFF.
    (If DPMS Situation in LFD, it operate Remocon regardless of set value).
    """
    CMD = 0x36
    GET, SET = True, True

    class IR_STATE(IntEnum):
        DISABLED = 0x00
        ENABLED = 0x01

    DATA = [IR_STATE]


class RGB_CONTRAST(Command):
    CMD = 0x37
    GET, SET = True, True
    DATA = [Int('CONTRAST', range(101))]


class RGB_BRIGHTNESS(Command):
    CMD = 0x38
    GET, SET = True, True
    DATA = [Int('BRIGHTNESS', range(101))]


class AUTO_ADJUSTMENT_ON(Command):
    CMD = 0x3D
    SUBCMD = 0x00
    GET, SET = False, True
    DATA = []


class COLOR_TONE(Command):
    CMD = 0x3E
    GET, SET = True, True

    class COLOR_TONE_STATE(IntEnum):
        COOL_2 = 0x00
        COOL_1 = 0x01
        NORMAL = 0x02
        WARM_1 = 0x03
        WARM_2 = 0x04
        OFF = 0x50

    DATA = [COLOR_TONE_STATE]


class COLOR_TEMPERATURE(Command):
    """
    Color temperature function.

    Unit is hectoKelvin (hK) (x*100 Kelvin) (example: 28 = 2800K).

    Supported values - 28, 30, 35, 40... 160.

    For older models: 0-10=(x*100K + 5000K), 253=2800K, 254=3000K, 255=4000K
    """
    CMD = 0x3F
    GET, SET = True, True

    DATA = [Int('HECTO_KELVIN')]


class STANDBY(Command):
    CMD = 0x4A
    GET, SET = True, True

    class STANDBY_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01
        AUTO = 0x02

    DATA = [STANDBY_STATE]


class AUTO_LAMP(Command):
    """
    Auto Lamp function (backlight).

    Note: When Manual Lamp Control is on,
    Auto Lamp Control will automatically turn off.
    """
    CMD = 0x57
    GET, SET = True, True

    DATA = [
        Time12H('MAX_TIME'),
        Int('MAX_LAMP_VALUE', range(101)),
        Time12H('MIN_TIME'),
        Int('MIN_LAMP_VALUE', range(101)),
    ]


class MANUAL_LAMP(Command):
    """
    Manual Lamp function (backlight).

    Note: When Auto Lamp Control is on,
    Manual Lamp Control will automatically turn off.
    """
    CMD = 0x58
    GET, SET = True, True
    DATA = [Int('LAMP_VALUE', range(101))]


class INVERSE(Command):
    CMD = 0x5A
    GET, SET = True, True

    class INVERSE_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [INVERSE_STATE]


class SAFETY_LOCK(Command):
    CMD = 0x5D
    GET, SET = True, True

    class LOCK_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [LOCK_STATE]


class PANEL_LOCK(Command):
    CMD = 0x5F
    GET, SET = True, True

    class LOCK_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [LOCK_STATE]


class CHANNEL_CHANGE(Command):
    CMD = 0x61
    GET, SET = False, True

    class CHANGE_TO(IntEnum):
        UP = 0x00
        DOWN = 0x01

    DATA = [CHANGE_TO]


class VOLUME_CHANGE(Command):
    CMD = 0x62
    GET, SET = False, True

    class CHANGE_TO(IntEnum):
        UP = 0x00
        DOWN = 0x01

    DATA = [CHANGE_TO]


class TICKER(Command):
    """
    Get/Set the device ticker. (Show text message overlay on the screen)

    Note: POS_HORIZ or POS_VERT are NONE in GET response
    if unsupported by the display.
    """
    CMD = 0x63
    GET, SET = True, True

    class POS_HORIZ(IntEnum):
        CENTER = 0x00
        LEFT = 0x01
        RIGHT = 0x02
        NONE = 0xFF

    class POS_VERTI(IntEnum):
        MIDDLE = 0x00
        TOP = 0x01
        BOTTOM = 0x02
        NONE = 0xFF

    class MOTION_DIR(IntEnum):
        LEFT = 0x00
        RIGHT = 0x01
        UP = 0x02
        DOWN = 0x03

    class MOTION_SPEED(IntEnum):
        NORMAL = 0x00
        SLOW = 0x01
        FAST = 0x02

    class FONT_SIZE(IntEnum):
        STANDARD = 0x00
        SMALL = 0x01
        LARGE = 0x02

    class FOREGROUND_COLOR(IntEnum):
        BLACK = 0x00
        WHITE = 0x01
        RED = 0x02
        GREEN = 0x03
        BLUE = 0x04
        YELLOW = 0x05
        MAGENTA = 0x06
        CYAN = 0x07

    class BACKGROUND_COLOR(IntEnum):
        BLACK = 0x00
        WHITE = 0x01
        RED = 0x02
        GREEN = 0x03
        BLUE = 0x04
        YELLOW = 0x05
        MAGENTA = 0x06
        CYAN = 0x07

    class FOREGROUND_OPACITY(IntEnum):
        FLASHING = 0x03
        FLASH_ALL = 0x04
        OFF = 0x05

    class BACKGROUND_OPACITY(IntEnum):
        SOLID = 0x00
        TRANSPARENT = 0x01
        TRANSLUCENT = 0x02
        UNKNOWN = 0x03

    DATA = [
        Bool('ON_OFF'),
        Time12H('START_TIME'),
        Time12H('END_TIME'),
        POS_HORIZ,
        POS_VERTI,
        Bool('MOTION_ON_OFF'),
        MOTION_DIR,
        MOTION_SPEED,
        FONT_SIZE,
        FOREGROUND_COLOR,
        BACKGROUND_COLOR,
        FOREGROUND_OPACITY,
        BACKGROUND_OPACITY,
        Str('MESSAGE')
    ]


class DEVICE_NAME(Command):
    """
    It reads the device name which user set up in network.
    Shows the information about entered device name.
    """
    CMD = 0x67
    GET, SET = True, False
    DATA = [Str('DEVICE_NAME')]


class OSD(Command):
    """
    Turns OSD (On-screen display) on/off.
    """
    CMD = 0x70
    GET, SET = True, True

    DATA = [Bool('OSD_ENABLED')]


class PICTURE_MODE(Command):
    CMD = 0x71
    GET, SET = True, True

    class PICTURE_MODE_STATE(IntEnum):
        DYNAMIC = 0x00
        STANDARD = 0x01
        MOVIE = 0x02
        CUSTOM_TV = 0x03
        NATURAL = 0x04
        CALIBRATION_TV = 0x05
        ENTERTAIN = 0x10
        INTERNET = 0x11
        TEXT = 0x12
        CUSTOM = 0x13
        ADVERTISEMENT = 0x14
        INFORMATION = 0x15
        CALIBRATION = 0x16
        SHOP_MALL_VIDEO = 0x20
        SHOP_MALL_TEXT = 0x21
        OFFICE_SCHOOL_VIDEO = 0x22
        OFFICE_SCHOOL_TEXT = 0x23
        TERMINAL_STATION_VIDEO = 0x24
        TERMINAL_STATION_TEXT = 0x25
        VIDEO_WALL_VIDEO = 0x26
        VIDEO_WALL_TEXT = 0x27
        HDR_PLUS = 0x30
        OFF = 0x50
        RESERVED_OTHER = 0x90

    DATA = [PICTURE_MODE_STATE]


class SOUND_MODE(Command):
    CMD = 0x72
    GET, SET = True, True

    class SOUND_MODE_STATE(IntEnum):
        STANDARD = 0x00
        MUSIC = 0x01
        MOVIE = 0x02
        SPEECH = 0x03
        CUSTOM = 0x04
        AMPLIFY = 0x05
        OPTIMIZED = 0x06

    DATA = [SOUND_MODE_STATE]


class ALL_KEYS_LOCK(Command):
    """
    Turns both REMOCON and Panel Key Lock function on/off.

    Note: Can operate regardless of whether power is on/off.
    """

    # TODO: REMOCON? Remote Control?
    CMD = 0x77
    GET, SET = True, True

    class LOCK_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [LOCK_STATE]


class MODEL_NAME(Command):
    CMD = 0x8A
    GET, SET = True, False
    DATA = [Str('MODEL_NAME')]


class PANEL_ON_TIME(Command):
    """
    Get the device panel on total time.

    Return value increased every 10 mins. To get hours use "MIN10 / 6".
    """
    CMD = 0x83
    GET, SET = True, False
    DATA = [Int('MIN10', length=2, byteorder='big')]

    @classmethod
    def parse_response_data(cls, data):
        # looks like they increased length on newer models,
        # so we're trying to decoce anyway
        return (int.from_bytes(data, byteorder='big'),)


class ENERGY_SAVING(Command):
    CMD = 0x92
    GET, SET = True, True

    class ENERGY_SAVING_STATE(IntEnum):
        OFF = 0x00
        LOW = 0x01
        MEDIUM = 0x02
        HIGH = 0x03
        PICTURE_OFF = 0x04

    DATA = [ENERGY_SAVING_STATE]


class RESET(Command):
    CMD = 0x9F
    GET, SET = False, True

    class RESET_TARGET(IntEnum):
        PICTURE = 0x00
        SOUND = 0x01
        SETUP = 0x02  # (System reset)
        ALL = 0x03
        SCREEN_DISPLAY = 0x04

    DATA = [RESET_TARGET]


class OSD_TYPE(Command):
    """
    Turns OSD (On-screen display) specific message types on/off.
    """
    CMD = 0xA3
    GET, SET = True, True

    class OSD_TYPE(IntEnum):
        SOURCE = 0x00
        NOT_OPTIMUM_MODE = 0x01
        NO_SIGNAL = 0x02
        MDC = 0x03
        SCHEDULE_CHANNEL = 0x04

    DATA = [OSD_TYPE, Bool('OSD_ENABLED')]
    RESPONSE_DATA = [Bitmask(OSD_TYPE, 'OSD_STATUS')]


class TIMER_15(Command):
    """
    Integrated timer function (15 data-length version).

    Note: This depends on product and will not work on older versions.

    ON_TIME/OFF_TIME: turn ON/OFF display at specific time of day

    ON_ACTIVE/OFF_ACTIVE: if timer is not active, values are ignored,
    so there may be only OFF timer, ON timer, or both.

    REPEAT: On which day timer is enabled
    (combined with HOLIDAY_APPLY and MANUAL_WEEKDAY)
    """
    CMD = Int('TIMER_ID', range(1, 8))
    _TIMER_ID_CMD = [0xA4, 0xA5, 0xA6, 0xAB, 0xAC, 0xAD, 0xAE]
    GET, SET = True, True

    class TIMER_REPEAT(IntEnum):
        ONCE = 0x00
        EVERYDAY = 0x01
        MON_FRI = 0x02
        MON_SAT = 0x03
        SAT_SUN = 0x04
        MANUAL_WEEKDAY = 0x05

    class WEEKDAY(IntEnum):
        SUN = 0x00
        MON = 0x01
        TUE = 0x02
        WED = 0x03
        THU = 0x04
        FRI = 0x05
        SAT = 0x06
        # ignore_bit_7 = 7

    class HOLIDAY_APPLY(IntEnum):
        DONT_APPLY_BOTH = 0x00
        APPLY_BOTH = 0x01
        ON_TIMER_ONLY_APPLY = 0x02
        OFF_TIMER_ONLY_APPLY = 0x03

    DATA = [
        Time12H('ON_TIME'),
        Bool('ON_ENABLED'),

        Time12H('OFF_TIME'),
        Bool('OFF_ENABLED'),

        EnumField(TIMER_REPEAT, 'ON_REPEAT'),
        Bitmask(WEEKDAY, 'ON_MANUAL_WEEKDAY'),

        EnumField(TIMER_REPEAT, 'OFF_REPEAT'),
        Bitmask(WEEKDAY, 'OFF_MANUAL_WEEKDAY'),

        VOLUME.VOLUME,
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
    def parse_response_data(cls, data, *args, _timer_version_check=True,
                            **kwargs):
        if _timer_version_check and len(data) == 13:
            raise RuntimeError('13 data-length version of timer received, '
                               'use timer_13 instead')
        return super().parse_response_data(data, *args, **kwargs)

    @classmethod
    def get_order(cls):
        return (0xA4, cls.name)


class TIMER_13(TIMER_15):
    """
    Integrated timer function (13 data-length version).

    Note: This depends on product and will not work on newer versions.
    """
    DATA = [
        Time12H('ON_TIME'),
        Bool('ON_ENABLED'),

        Time12H('OFF_TIME'),
        Bool('OFF_ENABLED'),

        EnumField(TIMER_15.TIMER_REPEAT, 'REPEAT'),
        Bitmask(TIMER_15.WEEKDAY, 'MANUAL_WEEKDAY'),
        VOLUME.VOLUME,
        INPUT_SOURCE.INPUT_SOURCE_STATE,
        TIMER_15.HOLIDAY_APPLY,
    ]

    @classmethod
    def parse_response_data(cls, data, *args, **kwargs):
        if len(data) == 15:
            raise RuntimeError('15 data-length version of timer received, '
                               'use timer_15 instead')
        return super().parse_response_data(
            data, *args, _timer_version_check=False, **kwargs)


class CLOCK_S(Command):
    """
    Current time function (second precision).

    Note: This is for models developed after 2013.
    For older models see CLOCK_M function (minute precision).
    """
    GET, SET = True, True
    CMD = 0xC5

    DATA = [DateTime()]


class CLOCK_M(CLOCK_S):
    """
    Current time function (minute precision).

    Note: This is for models developed until 2013.
    For newer models see CLOCK_S function (seconds precision).
    """
    CMD = 0xA7

    DATA = [DateTime(seconds=False)]


class HOLIDAY_SET(Command):
    """
    Add/Delete the device holiday schedule with the holiday schedule itself
    start month/day and end month/day.

    Note: On DELETE_ALL all parameters should be 0x00.
    """
    CMD = 0xA8
    GET, SET = False, True

    class HOLIDAY_MANAGE(IntEnum):
        ADD = 0x00
        DELETE = 0x01
        DELETE_ALL = 0x02

    DATA = [
        HOLIDAY_MANAGE,
        Int('START_MONTH', range(13)),
        Int('START_DAY', range(32)),
        Int('END_MONTH', range(13)),
        Int('END_DAY', range(32)),
        ]


class HOLIDAY_GET(Command):
    """
    Get the device holiday schedule.

    If INDEX is not specified, returns total number of Holiday Information.
    """
    CMD = 0xA9
    GET, SET = True, True

    DATA = [
        Int('INDEX'),
    ]

    RESPONSE_EXTRA = [
        Int('START_MONTH'),
        Int('START_DAY'),
        Int('END_MONTH'),
        Int('END_DAY'),
    ]

    @classmethod
    def parse_response_data(cls, data):
        if data[1:] == bytes([0, 0, 0, 0]):
            # index was not specified,
            # so it's total number of holiday information
            return (int(data[0]),)
        return super().parse_response_data(data)


class VIRTUAL_REMOTE(Command):
    """
    This function support that MDC command can work same as remote control.

    Note: In a certain model, 0x79 CONTENT key works as HOME
    and 0x1F DISPLAY key works as INFO.
    """
    CMD = 0xB0
    GET, SET = False, True

    class KEY_CODE(IntEnum):
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
        KEY_DISPLAY = 0x1F  # or KEY_INFO
        KEY_DIGIT = 0x23
        KEY_PIP_TV_VIDEO = 0x24
        KEY_EXIT = 0x2D
        KEY_MAGICINFO = 0x30  # limited support
        KEY_REW = 0x45
        KEY_STOP = 0x46
        KEY_PLAY = 0x47
        KEY_FF = 0x48
        KEY_PAUSE = 0x4A
        KEY_TOOLS = 0x4B
        KEY_RETURN = 0x58
        KEY_MAGICINFO_LITE = 0x5B  # limited support
        KEY_CURSOR_UP = 0x60
        KEY_CURSOR_DOWN = 0x61
        KEY_CURSOR_RIGHT = 0x62
        KEY_CURSOR_LEFT = 0x65
        KEY_ENTER = 0x68
        KEY_RED = 0x6C
        KEY_LOCK = 0x77
        KEY_CONTENT = 0x79  # HOME
        DISCRET_POWER_OFF = 0x98
        KEY_3D = 0x9F

    # # Corresponding to MediaKey API
    # # https://docs.tizen.org/application/web/api/latest/device_api/mobile/tizen/mediakey.html  # noqa
    # class MEDIA_KEY_CODE(IntEnum):
    #     PLAY = KEY_CODE.KEY_PLAY
    #     STOP = KEY_CODE.KEY_STOP
    #     PAUSE = KEY_CODE.KEY_PAUSE
    #     # PREVIOUS = ??
    #     # NEXT = ??
    #     FAST_FORWARD = KEY_CODE.KEY_FF
    #     REWIND - KEY_CODE.KEY_REW
    #     # PLAY_PAUSE = ??

    DATA = [KEY_CODE]


class NETWORK_STANDBY(Command):
    CMD = 0xB5
    GET, SET = True, True

    class NETWORK_STANDBY_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [NETWORK_STANDBY_STATE]


class DST(Command):
    CMD = 0xB6
    GET, SET = True, True

    class DST_STATE(IntEnum):
        OFF = 0x00
        AUTO = 0x01
        MANUAL = 0x02

    class MONTH(IntEnum):
        JAN = 0x00
        FEB = 0x01
        MAR = 0x02
        APR = 0x03
        MAY = 0x04
        JUN = 0x05
        JUL = 0x06
        AUG = 0x07
        SEP = 0x08
        OCT = 0x09
        NOV = 0x0A
        DEC = 0x0B

    class WEEK(IntEnum):
        WEEK_1 = 0x00
        WEEK_2 = 0x01
        WEEK_3 = 0x02
        WEEK_4 = 0x03
        WEEK_LAST = 0x04

    class WEEKDAY(IntEnum):
        # NOTE: same as TIMER_15.WEEKDAY
        SUN = 0x00
        MON = 0x01
        TUE = 0x02
        WED = 0x03
        THU = 0x04
        FRI = 0x05
        SAT = 0x06

    class OFFSET(IntEnum):
        PLUS_1_00 = 0x00
        PLUS_2_00 = 0x01

    DATA = [
        DST_STATE,
        EnumField(MONTH, 'START_MONTH'),
        EnumField(WEEK, 'START_WEEK'),
        EnumField(WEEKDAY, 'START_WEEKDAY'),
        Time('START_TIME'),
        EnumField(MONTH, 'END_MONTH'),
        EnumField(WEEK, 'END_WEEK'),
        EnumField(WEEKDAY, 'END_WEEKDAY'),
        Time('END_TIME'),
        OFFSET,
    ]

    RESPONSE_EXTRA = [
        Bool('TUNER_SUPPORT'),
    ]


class AUTO_ID_SETTING(Command):
    CMD = 0xB8
    GET, SET = True, True

    class AUTO_ID_SETTING_STATE(IntEnum):
        START = 0x00
        END = 0x01

    DATA = [AUTO_ID_SETTING_STATE]


class DISPLAY_ID(Command):
    CMD = 0xB9
    GET, SET = False, True

    class DISPLAY_ID_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [DISPLAY_ID_STATE]


class AUTO_SOURCE_SWITCH(Command):
    CMD = 0xCA
    SUBCMD = 0x81
    GET, SET = True, True

    class AUTO_SOURCE_SWITCH_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [AUTO_SOURCE_SWITCH_STATE]


class AUTO_SOURCE(Command):
    CMD = 0xCA
    SUBCMD = 0x82
    GET, SET = True, True

    class PRIMARY_SOURCE_RECOVERY(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [
        PRIMARY_SOURCE_RECOVERY,
        EnumField(INPUT_SOURCE.INPUT_SOURCE_STATE, 'PRIMARY_SOURCE'),
        EnumField(INPUT_SOURCE.INPUT_SOURCE_STATE, 'SECONDARY_SOURCE')
    ]


class LAUNCHER_PLAY_VIA(Command):
    CMD = 0xC7
    SUBCMD = 0x81
    GET, SET = True, True

    class PLAY_VIA_MODE(IntEnum):
        MAGIC_INFO = 0x00
        URL_LAUNCHER = 0x01
        MAGIC_IWB = 0x02

    DATA = [PLAY_VIA_MODE]


class LAUNCHER_URL_ADDRESS(Command):
    CMD = 0xC7
    SUBCMD = 0x82
    GET, SET = True, True
    DATA = [Str('URL_ADDRESS')]


class OSD_MENU_ORIENTATION(Command):
    CMD = 0xC8
    SUBCMD = 0x81
    GET, SET = True, True
    DATA = [_COMMON.ORIENTATION_MODE_STATE]


class OSD_SOURCE_CONTENT_ORIENTATION(Command):
    CMD = 0xC8
    SUBCMD = 0x82
    GET, SET = True, True
    DATA = [_COMMON.ORIENTATION_MODE_STATE]


class OSD_ASPECT_RATIO(Command):
    """
    Get/Set the device aspect ratio under portrait mode
    which set the rotated screen to be full or original.
    """
    CMD = 0xC8
    SUBCMD = 0x83
    GET, SET = True, True

    class ASPECT_RATIO_STATE(IntEnum):
        FULL_SCREEN = 0x00
        ORIGINAL = 0x01

    DATA = [ASPECT_RATIO_STATE]


class OSD_PIP_ORIENTATION(Command):
    CMD = 0xC8
    SUBCMD = 0x84
    GET, SET = True, True
    DATA = [_COMMON.ORIENTATION_MODE_STATE]


class OSD_MENU_SIZE(Command):
    CMD = 0xC8
    SUBCMD = 0x85
    GET, SET = True, True

    class MENU_SIZE_STATE(IntEnum):
        ORIGINAL = 0x00
        MEDIUM = 0x01
        SMALL = 0x02

    DATA = [MENU_SIZE_STATE]


class PANEL(Command):
    CMD = 0xF9
    GET, SET = True, True

    class PANEL_STATE(IntEnum):
        ON = 0x00
        OFF = 0x01

    DATA = [PANEL_STATE]


class SCREEN_MUTE(Command):
    # Undocumented (as of Ver. 15 2020-11-06)
    # see https://github.com/vgavro/samsung-mdc/issues/19
    CMD = 0xFE
    SUBCMD = 0x51
    GET, SET = True, True

    class SCREEN_MUTE_STATUS(IntEnum):
        ON = 0x00
        OFF = 0xFF

    DATA = [SCREEN_MUTE_STATUS]


class STATUS(Command):
    """
    Get the device various state like power, volume, sound mute, input source,
    picture aspect ratio.

    Note:
    For no audio models volume and mute returns 0xFF (255).

    N_TIME_NF, F_TIME_NF: OnTime/OffTime ON/OFF value
    (old type timer, now it's always 0x00).
    """
    CMD = 0x00
    GET, SET = True, False
    DATA = [
        POWER.POWER_STATE, VOLUME.VOLUME, MUTE.MUTE_STATE,
        INPUT_SOURCE.INPUT_SOURCE_STATE, PICTURE_ASPECT.PICTURE_ASPECT_STATE,
        Int('N_TIME_NF'), Int('F_TIME_NF')
    ]


class VIDEO(Command):
    CMD = 0x04
    GET, SET = True, False
    DATA = [
        Int('CONTRAST', range(101)), Int('BRIGHTNESS', range(101)),
        Int('SHARPNESS', range(101)), Int('COLOR', range(101)),
        Int('TINT', range(101)), COLOR_TONE.COLOR_TONE_STATE,
        Int('COLOR_TEMPERATURE'), Int('_IGNORE', range(1)),
    ]


class RGB(Command):
    CMD = 0x06
    GET, SET = True, False
    DATA = [
        Int('CONTRAST', range(101)), Int('BRIGHTNESS', range(101)),
        COLOR_TONE.COLOR_TONE_STATE, Int('COLOR_TEMPERATURE'),
        Int('_IGNORE', range(1)),
        Int('RED_GAIN'), Int('GREEN_GAIN'), Int('BLUE_GAIN'),
    ]


class VIDEO_WALL_STATE(Command):
    """
    Get/Set the device in video wall state.
    This will split the primary input source into smaller N number of squares
    and display them instead.

    Note: The device needs to be capable of this operation.
    Usually a primary high resolution source signal is daisy chained
    to lower resolution displays in a video wall using HDMI/DP.
    """
    CMD = 0x84
    GET, SET = True, True

    class VIDEO_WALL_STATE(IntEnum):
        OFF = 0x00
        ON = 0x01

    DATA = [VIDEO_WALL_STATE]


class VIDEO_WALL_MODE(Command):
    """
    Get/Set the device in aspect ratio of the video wall.

    FULL: stretch input source to fill display

    NATURAL: Keep aspect ratio of input source; do not fill display.

    Note: Needs VIDEO_WALL_STATE to be ON.
    """
    CMD = 0x5C
    GET, SET = True, True

    class VIDEO_WALL_MODE(IntEnum):
        NATURAL = 0x00
        FULL = 0x01

    DATA = [VIDEO_WALL_MODE]


class VIDEO_WALL_MODEL(Command):
    """
    Get/Set video wall model.

    MODEL: Size of the wall in (x, y) coordinates; ie. "2,2" or "4,1"

    SERIAL: Serial number - position of the display in the video wall,
    counting from the first display.

    Note: Needs VIDEO_WALL_STATE to be ON.
    """
    CMD = 0x89
    GET, SET = True, True

    DATA = [VideoWallModel('MODEL'), Int('SERIAL', range(1, 256))]
