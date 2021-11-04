# Samsung-MDC

This is implementation of Samsung MDC (Multiple Display Control) protocol on **python3.7+** and **asyncio** with most comprehensive CLI (command line interface).

It allows you to control a variety of different sources (TV, Monitor) through the built-in RS-232C or Ethernet interface.

[MDC Protocol specification - v15.0 2020-11-06](https://vgavro.github.io/samsung-mdc/MDC-Protocol.pdf)

* Implemented *{{command_count}}* commands
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
{{usage}}

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
{{python_example}}
```
