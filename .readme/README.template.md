# Samsung-MDC

This is implementation of Samsung MDC (Multiple Display Control) protocol on **python3.7+** and **asyncio** with most comprehensive CLI (command line interface).

It allows you to control a variety of different sources (TV, Monitor) through the built-in RS-232C or Ethernet interface.

[MDC Protocol specification - v13.7c 2016-02-23](https://vgavro.github.io/samsung-mdc/MDC-Protocol_v13.7c_2016-02-23.pdf)

* Implemented *{{command_count}}* commands
* Easy to extend using simple declarative API - see [samsung_mdc/commmands.py](https://github.com/vgavro/samsung-mdc/blob/master/samsung_mdc/commands.py)
* Detailed [CLI](#usage) help and parameters validation
* Run commands async on numerous targets (using asyncio)
* TCP and SERIAL mode (for RJ45 and RS232C connection types)
* [script](#script) command for advanced usage
* [Python example](#python-example)

Not implemented: some more commands (PRs are welcome)

## Install<a id="install"></a>

```
# global
pip3 install git+https://github.com/vgavro/samsung-mdc
samsung-mdc --help

# local
git clone https://github.com/vgavro/samsung-mdc
cd ./samsung-mdc
python3 -m venv venv
./venv/bin/pip3 install -e ./
./venv/bin/samsung-mdc --help
```

### Windows install <a id="windows-install"></a>
1. Install Git && Git Bash: https://git-scm.com/download/win
2. Install Python 3 latest release (tested with 3.9): https://www.python.org/downloads/windows/
3. Run "Git Bash", type in console:
```
pip3 install git+https://github.com/vgavro/samsung-mdc

# NOTE: python "Scripts" folder is not in %PATH% in Windows by default,
# so you may want to create alias for Git Bash
echo alias samsung-mdc=\'$(cygpath $(python -m site --user-site))/../Scripts/samsung-mdc.exe\' > ~/.bash_profile
source ~/.bash_profile

# test it
samsung-mdc --help
```

## Usage<a id="usage"></a>
{{usage}}

## Python example<a id="python-example"></a>
```python3
{{python_example}}
```
