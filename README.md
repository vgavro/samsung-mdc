# Samsung-MDC

This is implementation of Samsung MDC (Multiple Display Control) protocol on **python3.7+** and **asyncio** with most comprehensive CLI (command line interface).

It allows you to control a variety of different sources (TV, Monitor) through the built-in RS-232C or Ethernet interface.

[MDC Protocol specification - v15.0 2020-11-06](https://vgavro.github.io/samsung-mdc/MDC-Protocol.pdf)

* Implemented *70* commands
* Easy to extend using simple declarative API - see [samsung_mdc/commands.py](https://github.com/vgavro/samsung-mdc/blob/master/samsung_mdc/commands.py)
* Detailed [CLI](#usage) help and parameters validation
* Run commands async on numerous targets (using asyncio)
* TCP and SERIAL mode (for RJ45 and RS232C connection types)
* TCP over TLS mode ("Secured Protocol" using PIN)
* [script](#script) command for advanced usage
* [Python example](#python-example)

Not implemented: some more commands (PRs are welcome)

Also see: [Samsung MDC Unified](http://www.samsung-mcloud.com/02_Software/04_Tools/MDC/v1235/) - Reference Application (GUI, Windows) with partially implemented functionality.

## Install<a id="install"></a>

```
# global install/upgrade
sudo pip3 install --upgrade python-samsung-mdc
samsung-mdc --help

# local
git clone https://github.com/vgavro/samsung-mdc
cd ./samsung-mdc
python3 -m venv venv
./venv/bin/pip3 install -e ./
./venv/bin/samsung-mdc --help
```

### Windows install<a id="windows-install"></a>
1. Install Git && Git Bash: https://git-scm.com/download/win
2. Install Python 3 latest release (tested with 3.9): https://www.python.org/downloads/windows/
3. Run "Git Bash", type in console:

```
pip3 install --upgrade python-samsung-mdc

# NOTE: python "Scripts" folder is not in %PATH% in Windows by default,
# so you may want to create alias for Git Bash
echo alias samsung-mdc=\'python3 -m samsung_mdc\' >> ~/.bash_profile
source ~/.bash_profile

# test it
samsung-mdc --help
```

## Usage<a id="usage"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET COMMAND [ARGS]...

  Try 'samsung-mdc --help COMMAND' for command info

  For multiple targets commands will be running async, so result order may
  differ.

  TARGET may be:

  DISPLAY_ID@IP[:PORT] (default port: 1515, example: 0@192.168.0.10:1515)
  FILENAME with target list (separated by newline)

  For serial port connection:
  DISPLAY_ID@PORT_NAME for Windows (example: 1@COM1)
  DISPLAY_ID@PORT_PATH (example: 1@/dev/ttyUSB0)

  We're trying to make autodetection of connection mode by port name, but you
  may want to use --mode option.

Options:
  --version                     Show the version and exit.
  -v, --verbose
  -m, --mode [auto|tcp|serial]  default: auto
  -p, --pin INTEGER             4-digit PIN for secured TLS connection. If PIN
                                provided, "Secured Protocol" must be enabled
                                on remote device.
  -t, --timeout FLOAT           read/write/connect timeout in seconds
                                (default: 5) (connect can be overridden with
                                separate option)
  --connect-timeout FLOAT
  -h, --help                    Show this message and exit.

```
### Commands:

* [status](#status) `(POWER_STATE VOLUME MUTE_STATE INPUT_SOURCE_STATE PICTURE_ASPECT_STATE N_TIME_NF F_TIME_NF)`
* [video](#video) `(CONTRAST BRIGHTNESS SHARPNESS COLOR TINT COLOR_TONE_STATE COLOR_TEMPERATURE _IGNORE)`
* [rgb](#rgb) `(CONTRAST BRIGHTNESS COLOR_TONE_STATE COLOR_TEMPERATURE _IGNORE RED_GAIN GREEN_GAIN BLUE_GAIN)`
* [serial_number](#serial_number) `(SERIAL_NUMBER)`
* [error_status](#error_status) `(LAMP_ERROR_STATE TEMPERATURE_ERROR_STATE BRIGHTNESS_SENSOR_ERROR_STATE INPUT_SOURCE_ERROR_STATE TEMPERATURE FAN_ERROR_STATE)`
* [software_version](#software_version) `(SOFTWARE_VERSION)`
* [model_number](#model_number) `(MODEL_SPECIES MODEL_CODE TV_SUPPORT)`
* [power](#power) `[POWER_STATE]`
* [volume](#volume) `[VOLUME]`
* [mute](#mute) `[MUTE_STATE]`
* [input_source](#input_source) `[INPUT_SOURCE_STATE]`
* [picture_aspect](#picture_aspect) `[PICTURE_ASPECT_STATE]`
* [screen_mode](#screen_mode) `[SCREEN_MODE_STATE]`
* [screen_size](#screen_size) `(INCHES)`
* [network_configuration](#network_configuration) `[IP_ADDRESS SUBNET_MASK GATEWAY_ADDRESS DNS_SERVER_ADDRESS]`
* [network_mode](#network_mode) `[NETWORK_MODE_STATE]`
* [weekly_restart](#weekly_restart) `[WEEKDAY TIME]`
* [magicinfo_server](#magicinfo_server) `[MAGICINFO_SERVER_URL]`
* [mdc_connection](#mdc_connection) `[MDC_CONNECTION_TYPE]`
* [contrast](#contrast) `[CONTRAST]`
* [brightness](#brightness) `[BRIGHTNESS]`
* [sharpness](#sharpness) `[SHARPNESS]`
* [color](#color) `[COLOR]`
* [tint](#tint) `[TINT]`
* [h_position](#h_position) `H_POSITION_MOVE_TO`
* [v_position](#v_position) `V_POSITION_MOVE_TO`
* [auto_power](#auto_power) `[AUTO_POWER_STATE]`
* [clear_menu](#clear_menu) 
* [ir_state](#ir_state) `[IR_STATE]`
* [rgb_contrast](#rgb_contrast) `[CONTRAST]`
* [rgb_brightness](#rgb_brightness) `[BRIGHTNESS]`
* [auto_adjustment_on](#auto_adjustment_on) 
* [color_tone](#color_tone) `[COLOR_TONE_STATE]`
* [color_temperature](#color_temperature) `[HECTO_KELVIN]`
* [standby](#standby) `[STANDBY_STATE]`
* [auto_lamp](#auto_lamp) `[MAX_TIME MAX_LAMP_VALUE MIN_TIME MIN_LAMP_VALUE]`
* [manual_lamp](#manual_lamp) `[LAMP_VALUE]`
* [inverse](#inverse) `[INVERSE_STATE]`
* [video_wall_mode](#video_wall_mode) `[VIDEO_WALL_MODE]`
* [safety_lock](#safety_lock) `[LOCK_STATE]`
* [panel_lock](#panel_lock) `[LOCK_STATE]`
* [channel_change](#channel_change) `CHANGE_TO`
* [volume_change](#volume_change) `CHANGE_TO`
* [device_name](#device_name) `(DEVICE_NAME)`
* [osd](#osd) `[OSD_ENABLED]`
* [all_keys_lock](#all_keys_lock) `[LOCK_STATE]`
* [video_wall_state](#video_wall_state) `[VIDEO_WALL_STATE]`
* [video_wall_model](#video_wall_model) `[MODEL SERIAL]`
* [model_name](#model_name) `(MODEL_NAME)`
* [energy_saving](#energy_saving) `[ENERGY_SAVING_STATE]`
* [reset](#reset) `RESET_TARGET`
* [osd_type](#osd_type) `[OSD_TYPE OSD_ENABLED]`
* [timer_13](#timer_13) `TIMER_ID [ON_TIME ON_ENABLED OFF_TIME OFF_ENABLED REPEAT MANUAL_WEEKDAY VOLUME INPUT_SOURCE_STATE HOLIDAY_APPLY]`
* [timer_15](#timer_15) `TIMER_ID [ON_TIME ON_ENABLED OFF_TIME OFF_ENABLED ON_REPEAT ON_MANUAL_WEEKDAY OFF_REPEAT OFF_MANUAL_WEEKDAY VOLUME INPUT_SOURCE_STATE HOLIDAY_APPLY]`
* [clock_m](#clock_m) `[DATETIME]`
* [holiday_set](#holiday_set) `HOLIDAY_MANAGE START_MONTH START_DAY END_MONTH END_DAY`
* [holiday_get](#holiday_get) `[INDEX]`
* [virtual_remote](#virtual_remote) `KEY_CODE`
* [network_standby](#network_standby) `[NETWORK_STANDBY_STATE]`
* [dst](#dst) `[DST_STATE START_MONTH START_WEEK START_WEEKDAY START_TIME END_MONTH END_WEEK END_WEEKDAY END_TIME OFFSET]`
* [auto_id_setting](#auto_id_setting) `[AUTO_ID_SETTING_STATE]`
* [display_id](#display_id) `DISPLAY_ID_STATE`
* [clock_s](#clock_s) `[DATETIME]`
* [launcher_play_via](#launcher_play_via) `[PLAY_VIA_MODE]`
* [launcher_url_address](#launcher_url_address) `[URL_ADDRESS]`
* [auto_source_switch](#auto_source_switch) `[AUTO_SOURCE_SWITCH_STATE]`
* [auto_source](#auto_source) `[PRIMARY_SOURCE_RECOVERY PRIMARY_SOURCE SECONDARY_SOURCE]`
* [panel](#panel) `[PANEL_STATE]`
* [script](#script) `[OPTIONS] SCRIPT_FILE`
* [raw](#raw) `[OPTIONS] COMMAND [DATA]`

#### status<a id="status"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET status

  Get the device various state like power, volume, sound mute, input source,
  picture aspect ratio.

  Note: For no audio models volume and mute returns 0xFF (255).

  N_TIME_NF, F_TIME_NF: OnTime/OffTime ON/OFF value (old type timer, now it's
  always 0x00).

Data:
  POWER_STATE           OFF | ON | REBOOT
  VOLUME                int (0-100)
  MUTE_STATE            OFF | ON | NONE
  INPUT_SOURCE_STATE    NONE | S_VIDEO | COMPONENT | AV | AV2 | SCART1 | DVI |
                        PC | BNC | DVI_VIDEO | MAGIC_INFO | HDMI1 | HDMI1_PC |
                        HDMI2 | HDMI2_PC | DISPLAY_PORT_1 | DISPLAY_PORT_2 |
                        DISPLAY_PORT_3 | RF_TV | HDMI3 | HDMI3_PC | HDMI4 |
                        HDMI4_PC | TV_DTV | PLUG_IN_MODE | HD_BASE_T |
                        MEDIA_MAGIC_INFO_S | WIDI_SCREEN_MIRRORING |
                        INTERNAL_USB | URL_LAUNCHER | IWB
  PICTURE_ASPECT_STATE  PC_16_9 | PC_4_3 | PC_ORIGINAL_RATIO | PC_21_9 |
                        VIDEO_AUTO_WIDE | VIDEO_16_9 | VIDEO_ZOOM |
                        VIDEO_ZOOM_1 | VIDEO_ZOOM_2 | VIDEO_SCREEN_FIT |
                        VIDEO_4_3 | VIDEO_WIDE_FIT | VIDEO_CUSTOM |
                        VIDEO_SMART_VIEW_1 | VIDEO_SMART_VIEW_2 |
                        VIDEO_WIDE_ZOOM | VIDEO_21_9
  N_TIME_NF             int
  F_TIME_NF             int
```
#### video<a id="video"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET video

Data:
  CONTRAST           int (0-100)
  BRIGHTNESS         int (0-100)
  SHARPNESS          int (0-100)
  COLOR              int (0-100)
  TINT               int (0-100)
  COLOR_TONE_STATE   COOL_2 | COOL_1 | NORMAL | WARM_1 | WARM_2 | OFF
  COLOR_TEMPERATURE  int
  _IGNORE            int (0-0)
```
#### rgb<a id="rgb"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET rgb

Data:
  CONTRAST           int (0-100)
  BRIGHTNESS         int (0-100)
  COLOR_TONE_STATE   COOL_2 | COOL_1 | NORMAL | WARM_1 | WARM_2 | OFF
  COLOR_TEMPERATURE  int
  _IGNORE            int (0-0)
  RED_GAIN           int
  GREEN_GAIN         int
  BLUE_GAIN          int
```
#### serial_number<a id="serial_number"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET serial_number

Data:
  SERIAL_NUMBER  str
```
#### error_status<a id="error_status"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET error_status

Data:
  LAMP_ERROR_STATE               NORMAL | ERROR
  TEMPERATURE_ERROR_STATE        NORMAL | ERROR
  BRIGHTNESS_SENSOR_ERROR_STATE  NONE | ERROR | NORMAL
  INPUT_SOURCE_ERROR_STATE       NORMAL | ERROR | INVALID
  TEMPERATURE                    int
  FAN_ERROR_STATE                NORMAL | ERROR | NONE
```
#### software_version<a id="software_version"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET software_version

Data:
  SOFTWARE_VERSION  str
```
#### model_number<a id="model_number"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET model_number

Data:
  MODEL_SPECIES  PDP | LCD | DLP | LED | CRT | OLED
  MODEL_CODE     int
  TV_SUPPORT     SUPPORTED | NOT_SUPPORTED
```
#### power<a id="power"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET power [POWER_STATE]

Data:
  POWER_STATE  OFF | ON | REBOOT
```
#### volume<a id="volume"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET volume [VOLUME]

Data:
  VOLUME  int (0-100)
```
#### mute<a id="mute"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET mute [MUTE_STATE]

Data:
  MUTE_STATE  OFF | ON | NONE
```
#### input_source<a id="input_source"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET input_source [INPUT_SOURCE_STATE]

Data:
  INPUT_SOURCE_STATE  NONE | S_VIDEO | COMPONENT | AV | AV2 | SCART1 | DVI |
                      PC | BNC | DVI_VIDEO | MAGIC_INFO | HDMI1 | HDMI1_PC |
                      HDMI2 | HDMI2_PC | DISPLAY_PORT_1 | DISPLAY_PORT_2 |
                      DISPLAY_PORT_3 | RF_TV | HDMI3 | HDMI3_PC | HDMI4 |
                      HDMI4_PC | TV_DTV | PLUG_IN_MODE | HD_BASE_T |
                      MEDIA_MAGIC_INFO_S | WIDI_SCREEN_MIRRORING |
                      INTERNAL_USB | URL_LAUNCHER | IWB
```
#### picture_aspect<a id="picture_aspect"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET picture_aspect [PICTURE_ASPECT_STATE]

Data:
  PICTURE_ASPECT_STATE  PC_16_9 | PC_4_3 | PC_ORIGINAL_RATIO | PC_21_9 |
                        VIDEO_AUTO_WIDE | VIDEO_16_9 | VIDEO_ZOOM |
                        VIDEO_ZOOM_1 | VIDEO_ZOOM_2 | VIDEO_SCREEN_FIT |
                        VIDEO_4_3 | VIDEO_WIDE_FIT | VIDEO_CUSTOM |
                        VIDEO_SMART_VIEW_1 | VIDEO_SMART_VIEW_2 |
                        VIDEO_WIDE_ZOOM | VIDEO_21_9
```
#### screen_mode<a id="screen_mode"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET screen_mode [SCREEN_MODE_STATE]

Data:
  SCREEN_MODE_STATE  MODE_16_9 | MODE_ZOOM | MODE_4_3 | MODE_WIDE_ZOOM
```
#### screen_size<a id="screen_size"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET screen_size

Data:
  INCHES  int (0-255)
```
#### network_configuration<a id="network_configuration"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET network_configuration [IP_ADDRESS
                   SUBNET_MASK GATEWAY_ADDRESS DNS_SERVER_ADDRESS]

Data:
  IP_ADDRESS          IP address
  SUBNET_MASK         IP address
  GATEWAY_ADDRESS     IP address
  DNS_SERVER_ADDRESS  IP address
```
#### network_mode<a id="network_mode"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET network_mode [NETWORK_MODE_STATE]

Data:
  NETWORK_MODE_STATE  DYNAMIC | STATIC
```
#### weekly_restart<a id="weekly_restart"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET weekly_restart [WEEKDAY TIME]

Data:
  WEEKDAY  list(,) SUN | SAT | FRI | THU | WED | TUE | MON
  TIME     time (format: %H:%M:%S)
```
#### magicinfo_server<a id="magicinfo_server"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET magicinfo_server [MAGICINFO_SERVER_URL]

  MagicInfo Server URL (example: "http://example.com:80")

Data:
  MAGICINFO_SERVER_URL  str
```
#### mdc_connection<a id="mdc_connection"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET mdc_connection [MDC_CONNECTION_TYPE]

  Note: Depends on the product specification, if it is set as RJ45 then serial
  MDC will not work.

Data:
  MDC_CONNECTION_TYPE  RS232C | RJ45
```
#### contrast<a id="contrast"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET contrast [CONTRAST]

Data:
  CONTRAST  int (0-100)
```
#### brightness<a id="brightness"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET brightness [BRIGHTNESS]

Data:
  BRIGHTNESS  int (0-100)
```
#### sharpness<a id="sharpness"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET sharpness [SHARPNESS]

Data:
  SHARPNESS  int (0-100)
```
#### color<a id="color"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET color [COLOR]

Data:
  COLOR  int (0-100)
```
#### tint<a id="tint"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET tint [TINT]

  Tint value code to be set on TV/Monitor. R: Tint Value, G: ( 100 - Tint )
  Value.

  Note: Tint could only be set in 50 Steps (0, 2, 4, 6... 100).

Data:
  TINT  int (0-100)
```
#### h_position<a id="h_position"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET h_position H_POSITION_MOVE_TO

Data:
  H_POSITION_MOVE_TO  LEFT | RIGHT
```
#### v_position<a id="v_position"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET v_position V_POSITION_MOVE_TO

Data:
  V_POSITION_MOVE_TO  UP | DOWN
```
#### auto_power<a id="auto_power"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET auto_power [AUTO_POWER_STATE]

Data:
  AUTO_POWER_STATE  OFF | ON
```
#### clear_menu<a id="clear_menu"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET clear_menu
```
#### ir_state<a id="ir_state"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET ir_state [IR_STATE]

  Enables/disables IR (Infrared) receiving function (Remote Control).

  Working Condition: * Can operate regardless of whether power is ON/OFF. (If
  DPMS Situation in LFD, it operate Remocon regardless of set value).

Data:
  IR_STATE  DISABLED | ENABLED
```
#### rgb_contrast<a id="rgb_contrast"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET rgb_contrast [CONTRAST]

Data:
  CONTRAST  int (0-100)
```
#### rgb_brightness<a id="rgb_brightness"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET rgb_brightness [BRIGHTNESS]

Data:
  BRIGHTNESS  int (0-100)
```
#### auto_adjustment_on<a id="auto_adjustment_on"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET auto_adjustment_on
```
#### color_tone<a id="color_tone"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET color_tone [COLOR_TONE_STATE]

Data:
  COLOR_TONE_STATE  COOL_2 | COOL_1 | NORMAL | WARM_1 | WARM_2 | OFF
```
#### color_temperature<a id="color_temperature"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET color_temperature [HECTO_KELVIN]

  Color temperature function.

  Unit is hectoKelvin (hK) (x*100 Kelvin) (example: 28 = 2800K).

  Supported values - 28, 30, 35, 40... 160.

  For older models: 0-10=(x*100K + 5000K), 253=2800K, 254=3000K, 255=4000K

Data:
  HECTO_KELVIN  int
```
#### standby<a id="standby"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET standby [STANDBY_STATE]

Data:
  STANDBY_STATE  OFF | ON | AUTO
```
#### auto_lamp<a id="auto_lamp"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET auto_lamp [MAX_TIME MAX_LAMP_VALUE
                   MIN_TIME MIN_LAMP_VALUE]

  Auto Lamp function (backlight).

  Note: When Manual Lamp Control is on, Auto Lamp Control will automatically
  turn off.

Data:
  MAX_TIME        time (format: %H:%M:%S)
  MAX_LAMP_VALUE  int (0-100)
  MIN_TIME        time (format: %H:%M:%S)
  MIN_LAMP_VALUE  int (0-100)
```
#### manual_lamp<a id="manual_lamp"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET manual_lamp [LAMP_VALUE]

  Manual Lamp function (backlight).

  Note: When Auto Lamp Control is on, Manual Lamp Control will automatically
  turn off.

Data:
  LAMP_VALUE  int (0-100)
```
#### inverse<a id="inverse"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET inverse [INVERSE_STATE]

Data:
  INVERSE_STATE  OFF | ON
```
#### video_wall_mode<a id="video_wall_mode"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET video_wall_mode [VIDEO_WALL_MODE]

  Get or set the device in aspect ratio of the video wall.

  FULL: stretch input source to fill display

  NATURAL: Keep aspect ratio of input source; do not fill display.

  Note: Needs VIDEO_WALL_STATE to be ON.

Data:
  VIDEO_WALL_MODE  NATURAL | FULL
```
#### safety_lock<a id="safety_lock"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET safety_lock [LOCK_STATE]

Data:
  LOCK_STATE  OFF | ON
```
#### panel_lock<a id="panel_lock"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET panel_lock [LOCK_STATE]

Data:
  LOCK_STATE  OFF | ON
```
#### channel_change<a id="channel_change"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET channel_change CHANGE_TO

Data:
  CHANGE_TO  UP | DOWN
```
#### volume_change<a id="volume_change"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET volume_change CHANGE_TO

Data:
  CHANGE_TO  UP | DOWN
```
#### device_name<a id="device_name"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET device_name

  It reads the device name which user set up in network. Shows the information
  about entered device name.

Data:
  DEVICE_NAME  str
```
#### osd<a id="osd"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET osd [OSD_ENABLED]

  Turns OSD (On-screen display) on/off.

Data:
  OSD_ENABLED  bool
```
#### all_keys_lock<a id="all_keys_lock"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET all_keys_lock [LOCK_STATE]

  Turns both REMOCON and Panel Key Lock function on/off.

  Note: Can operate regardless of whether power is on/off.

Data:
  LOCK_STATE  OFF | ON
```
#### video_wall_state<a id="video_wall_state"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET video_wall_state [VIDEO_WALL_STATE]

  Get or set the device in video wall state. This will split the primary input
  source into smaller N number of squares and display them instead.

  Note: The device needs to be capable of this operation. Usually a primary
  high resolution source signal is daisy chained to lower resolution displays
  in a video wall using HDMI/DP.

Data:
  VIDEO_WALL_STATE  OFF | ON
```
#### video_wall_model<a id="video_wall_model"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET video_wall_model [MODEL SERIAL]

  Get or set video wall model.

  MODEL: Size of the wall in (x, y) coordinates; ie. "2,2" or "4,1"

  SERIAL: Serial number - position of the display in the video wall, counting
  from the first display.

  Note: Needs VIDEO_WALL_STATE to be ON.

Data:
  MODEL   Video Wall model (format: X,Y eg. 4,5)
  SERIAL  int (1-255)
```
#### model_name<a id="model_name"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET model_name

Data:
  MODEL_NAME  str
```
#### energy_saving<a id="energy_saving"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET energy_saving [ENERGY_SAVING_STATE]

Data:
  ENERGY_SAVING_STATE  OFF | LOW | MEDIUM | HIGH | PICTURE_OFF
```
#### reset<a id="reset"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET reset RESET_TARGET

Data:
  RESET_TARGET  PICTURE | SOUND | SETUP | ALL | SCREEN_DISPLAY
```
#### osd_type<a id="osd_type"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET osd_type [OSD_TYPE OSD_ENABLED]

  Turns OSD (On-screen display) specific message types on/off.

Data:
  OSD_TYPE     SOURCE | NOT_OPTIMUM_MODE | NO_SIGNAL | MDC | SCHEDULE_CHANNEL
  OSD_ENABLED  bool
```
#### timer_13<a id="timer_13"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET timer_13 TIMER_ID [ON_TIME ON_ENABLED
                   OFF_TIME OFF_ENABLED REPEAT MANUAL_WEEKDAY VOLUME
                   INPUT_SOURCE_STATE HOLIDAY_APPLY]

  Integrated timer function (13 data-length version).

  Note: This depends on product and will not work on newer versions.

Data:
  TIMER_ID            int (1-7)
  ON_TIME             time (format: %H:%M:%S)
  ON_ENABLED          bool
  OFF_TIME            time (format: %H:%M:%S)
  OFF_ENABLED         bool
  REPEAT              ONCE | EVERYDAY | MON_FRI | MON_SAT | SAT_SUN |
                      MANUAL_WEEKDAY
  MANUAL_WEEKDAY      list(,) SUN | MON | TUE | WED | THU | FRI | SAT
  VOLUME              int (0-100)
  INPUT_SOURCE_STATE  NONE | S_VIDEO | COMPONENT | AV | AV2 | SCART1 | DVI |
                      PC | BNC | DVI_VIDEO | MAGIC_INFO | HDMI1 | HDMI1_PC |
                      HDMI2 | HDMI2_PC | DISPLAY_PORT_1 | DISPLAY_PORT_2 |
                      DISPLAY_PORT_3 | RF_TV | HDMI3 | HDMI3_PC | HDMI4 |
                      HDMI4_PC | TV_DTV | PLUG_IN_MODE | HD_BASE_T |
                      MEDIA_MAGIC_INFO_S | WIDI_SCREEN_MIRRORING |
                      INTERNAL_USB | URL_LAUNCHER | IWB
  HOLIDAY_APPLY       DONT_APPLY_BOTH | APPLY_BOTH | ON_TIMER_ONLY_APPLY |
                      OFF_TIMER_ONLY_APPLY
```
#### timer_15<a id="timer_15"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET timer_15 TIMER_ID [ON_TIME ON_ENABLED
                   OFF_TIME OFF_ENABLED ON_REPEAT ON_MANUAL_WEEKDAY OFF_REPEAT
                   OFF_MANUAL_WEEKDAY VOLUME INPUT_SOURCE_STATE HOLIDAY_APPLY]

  Integrated timer function (15 data-length version).

  Note: This depends on product and will not work on older versions.

  ON_TIME/OFF_TIME: turn ON/OFF display at specific time of day

  ON_ACTIVE/OFF_ACTIVE: if timer is not active, values are ignored, so there
  may be only OFF timer, ON timer, or both.

  REPEAT: On which day timer is enabled (combined with HOLIDAY_APPLY and
  MANUAL_WEEKDAY)

Data:
  TIMER_ID            int (1-7)
  ON_TIME             time (format: %H:%M:%S)
  ON_ENABLED          bool
  OFF_TIME            time (format: %H:%M:%S)
  OFF_ENABLED         bool
  ON_REPEAT           ONCE | EVERYDAY | MON_FRI | MON_SAT | SAT_SUN |
                      MANUAL_WEEKDAY
  ON_MANUAL_WEEKDAY   list(,) SUN | MON | TUE | WED | THU | FRI | SAT
  OFF_REPEAT          ONCE | EVERYDAY | MON_FRI | MON_SAT | SAT_SUN |
                      MANUAL_WEEKDAY
  OFF_MANUAL_WEEKDAY  list(,) SUN | MON | TUE | WED | THU | FRI | SAT
  VOLUME              int (0-100)
  INPUT_SOURCE_STATE  NONE | S_VIDEO | COMPONENT | AV | AV2 | SCART1 | DVI |
                      PC | BNC | DVI_VIDEO | MAGIC_INFO | HDMI1 | HDMI1_PC |
                      HDMI2 | HDMI2_PC | DISPLAY_PORT_1 | DISPLAY_PORT_2 |
                      DISPLAY_PORT_3 | RF_TV | HDMI3 | HDMI3_PC | HDMI4 |
                      HDMI4_PC | TV_DTV | PLUG_IN_MODE | HD_BASE_T |
                      MEDIA_MAGIC_INFO_S | WIDI_SCREEN_MIRRORING |
                      INTERNAL_USB | URL_LAUNCHER | IWB
  HOLIDAY_APPLY       DONT_APPLY_BOTH | APPLY_BOTH | ON_TIMER_ONLY_APPLY |
                      OFF_TIMER_ONLY_APPLY
```
#### clock_m<a id="clock_m"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET clock_m [DATETIME]

  Current time function (minute precision).

  Note: This is for models developed until 2013. For newer models see CLOCK_S
  function (seconds precision).

Data:
  DATETIME  datetime (format: %Y-%m-%dT%H:%M:%S / %Y-%m-%d %H:%M:%S /
            %Y-%m-%dT%H:%M / %Y-%m-%d %H:%M)
```
#### holiday_set<a id="holiday_set"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET holiday_set HOLIDAY_MANAGE START_MONTH
                   START_DAY END_MONTH END_DAY

  Add/Delete the device holiday schedule with the holiday schedule itself
  start month/day and end month/day.

  Note: On DELETE_ALL all parameters should be 0x00.

Data:
  HOLIDAY_MANAGE  ADD | DELETE | DELETE_ALL
  START_MONTH     int (0-12)
  START_DAY       int (0-31)
  END_MONTH       int (0-12)
  END_DAY         int (0-31)
```
#### holiday_get<a id="holiday_get"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET holiday_get [INDEX]

  Get the device holiday schedule.

  If INDEX is not specified, returns total number of Holiday Information.

Data:
  INDEX  int

Response extra:
  START_MONTH  int
  START_DAY    int
  END_MONTH    int
  END_DAY      int
```
#### virtual_remote<a id="virtual_remote"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET virtual_remote KEY_CODE

  This function support that MDC command can work same as remote control.

  Note: In a certain model, 0x79 CONTENT key works as HOME and 0x1F DISPLAY
  key works as INFO.

Data:
  KEY_CODE  KEY_SOURCE | KEY_POWER | KEY_1 | KEY_2 | KEY_3 | KEY_VOLUME_UP |
            KEY_4 | KEY_5 | KEY_6 | KEY_VOLUME_DOWN | KEY_7 | KEY_8 | KEY_9 |
            KEY_MUTE | KEY_CHANNEL_DOWN | KEY_0 | KEY_CHANNEL_UP | KEY_GREEN |
            KEY_YELLOW | KEY_CYAN | KEY_MENU | KEY_DISPLAY | KEY_DIGIT |
            KEY_PIP_TV_VIDEO | KEY_EXIT | KEY_MAGICINFO | KEY_REW | KEY_STOP |
            KEY_PLAY | KEY_FF | KEY_PAUSE | KEY_TOOLS | KEY_RETURN |
            KEY_MAGICINFO_LITE | KEY_CURSOR_UP | KEY_CURSOR_DOWN |
            KEY_CURSOR_RIGHT | KEY_CURSOR_LEFT | KEY_ENTER | KEY_RED |
            KEY_LOCK | KEY_CONTENT | DISCRET_POWER_OFF | KEY_3D
```
#### network_standby<a id="network_standby"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET network_standby [NETWORK_STANDBY_STATE]

Data:
  NETWORK_STANDBY_STATE  OFF | ON
```
#### dst<a id="dst"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET dst [DST_STATE START_MONTH START_WEEK
                   START_WEEKDAY START_TIME END_MONTH END_WEEK END_WEEKDAY
                   END_TIME OFFSET]

Data:
  DST_STATE      OFF | AUTO | MANUAL
  START_MONTH    JAN | FEB | MAR | APR | MAY | JUN | JUL | AUG | SEP | OCT |
                 NOV | DEC
  START_WEEK     WEEK_1 | WEEK_2 | WEEK_3 | WEEK_4 | WEEK_LAST
  START_WEEKDAY  SUN | MON | TUE | WED | THU | FRI | SAT
  START_TIME     time (format: %H:%M:%S)
  END_MONTH      JAN | FEB | MAR | APR | MAY | JUN | JUL | AUG | SEP | OCT |
                 NOV | DEC
  END_WEEK       WEEK_1 | WEEK_2 | WEEK_3 | WEEK_4 | WEEK_LAST
  END_WEEKDAY    SUN | MON | TUE | WED | THU | FRI | SAT
  END_TIME       time (format: %H:%M:%S)
  OFFSET         PLUS_1_00 | PLUS_2_00

Response extra:
  TUNER_SUPPORT  bool
```
#### auto_id_setting<a id="auto_id_setting"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET auto_id_setting [AUTO_ID_SETTING_STATE]

Data:
  AUTO_ID_SETTING_STATE  START | END
```
#### display_id<a id="display_id"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET display_id DISPLAY_ID_STATE

Data:
  DISPLAY_ID_STATE  OFF | ON
```
#### clock_s<a id="clock_s"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET clock_s [DATETIME]

  Current time function (second precision).

  Note: This is for models developed after 2013. For older models see CLOCK_M
  function (minute precision).

Data:
  DATETIME  datetime (format: %Y-%m-%dT%H:%M:%S / %Y-%m-%d %H:%M:%S /
            %Y-%m-%dT%H:%M / %Y-%m-%d %H:%M)
```
#### launcher_play_via<a id="launcher_play_via"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET launcher_play_via [PLAY_VIA_MODE]

Data:
  PLAY_VIA_MODE  MAGIC_INFO | URL_LAUNCHER | MAGIC_IWB
```
#### launcher_url_address<a id="launcher_url_address"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET launcher_url_address [URL_ADDRESS]

Data:
  URL_ADDRESS  str
```
#### auto_source_switch<a id="auto_source_switch"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET auto_source_switch
                   [AUTO_SOURCE_SWITCH_STATE]

Data:
  AUTO_SOURCE_SWITCH_STATE  OFF | ON
```
#### auto_source<a id="auto_source"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET auto_source [PRIMARY_SOURCE_RECOVERY
                   PRIMARY_SOURCE SECONDARY_SOURCE]

Data:
  PRIMARY_SOURCE_RECOVERY  OFF | ON
  PRIMARY_SOURCE           NONE | S_VIDEO | COMPONENT | AV | AV2 | SCART1 |
                           DVI | PC | BNC | DVI_VIDEO | MAGIC_INFO | HDMI1 |
                           HDMI1_PC | HDMI2 | HDMI2_PC | DISPLAY_PORT_1 |
                           DISPLAY_PORT_2 | DISPLAY_PORT_3 | RF_TV | HDMI3 |
                           HDMI3_PC | HDMI4 | HDMI4_PC | TV_DTV | PLUG_IN_MODE
                           | HD_BASE_T | MEDIA_MAGIC_INFO_S |
                           WIDI_SCREEN_MIRRORING | INTERNAL_USB | URL_LAUNCHER
                           | IWB
  SECONDARY_SOURCE         NONE | S_VIDEO | COMPONENT | AV | AV2 | SCART1 |
                           DVI | PC | BNC | DVI_VIDEO | MAGIC_INFO | HDMI1 |
                           HDMI1_PC | HDMI2 | HDMI2_PC | DISPLAY_PORT_1 |
                           DISPLAY_PORT_2 | DISPLAY_PORT_3 | RF_TV | HDMI3 |
                           HDMI3_PC | HDMI4 | HDMI4_PC | TV_DTV | PLUG_IN_MODE
                           | HD_BASE_T | MEDIA_MAGIC_INFO_S |
                           WIDI_SCREEN_MIRRORING | INTERNAL_USB | URL_LAUNCHER
                           | IWB
```
#### panel<a id="panel"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET panel [PANEL_STATE]

Data:
  PANEL_STATE  ON | OFF
```
#### script<a id="script"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET script [OPTIONS] SCRIPT_FILE

  Script file with commands to execute.

  Commands for multiple targets will be running async, but commands order is
  preserved for device (and is running on same connection), exit on first fail
  unless retry options provided.

  It's highly recommended to use sleep option for virtual_remote!

  Additional commands:
  sleep SECONDS  (FLOAT, --sleep option for this command is ignored)
  disconnect

  Format:
  command1 [ARGS]...
  command2 [ARGS]...

  Example: samsung-mdc ./targets.txt script -s 3 -r 1 -v KEY enter ./commands.txt
  # commands.txt content
  power on
  sleep 5
  clear_menu
  virtual_remote key_menu
  virtual_remote key_down
  virtual_remote {{ KEY }}
  clear_menu

Arguments:
  script_file  Text file with commands, separated by newline.

Options:
  -s, --sleep FLOAT            Pause between commands (seconds)
  --retry-command INTEGER      Retry command if failed (count)
  --retry-command-sleep FLOAT  Sleep before command retry (seconds)
  -r, --retry-script INTEGER   Retry script if failed (count)
  --retry-script-sleep FLOAT   Sleep before script retry (seconds)
  --ignore-nak                 Ignore negative acknowledgement errors
  -v, --var NAME VALUE         Variable "{{ NAME }}" in script will be
                               replaced by VALUE
  --help                       Show this message and exit.
```
#### raw<a id="raw"></a>
```
Usage: samsung-mdc [OPTIONS] TARGET raw [OPTIONS] COMMAND [DATA]

  Helper command to send raw data for test purposes.

Arguments:
  command  Command and (optionally) subcommand (example: a1 or a1:b2)
  data     Data payload if any (example: a1:b2)
```

## Troubleshooting

### Finding DISPLAY ID

On most devices it's usually `0` or `1`. Some devices may use `255` (0xFF) or `254` (0xFE) as all/any display, but behavior in such cases for more than 1 display is undefined.

Display id can be found using remote control: `Home` -> `ID Settings`.

### NAKError

If you receive NAK errors on some commands, you may try to:

* Ensure that device is powered on and completely loaded
* Switch to input source HDMI1
* Reboot device
* Reset all settings
* Disable MagicINFO
* Factory reset (using "Service Menu")

## Python example<a id="python-example"></a>
```python3
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

```
