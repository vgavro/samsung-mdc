# Samsung-MDC

This is implementation of Samsung MDC (Multiple Display Control) protocol using python3.7+ and asyncio with most comprehensive CLI (command line interface).

It allows you to control a variety of different sources (TV, Monitor) through the built-in RS-232C or Ethernet interface.

[MDC Protocol specification - v13.7c 2016-02-23]('MDC Protocol 2015 v13.7c.pdf')

* Implemented *{{command_count}}* commands
* Easy to extend using simple declarative API - see [samsung_mdc/commmands.py](samsung_mdc/commands.py)
* Detailed CLI help and parameters validation
* Run commands async on numerous targets
* [script](#script) command for advanced usage

Not implemented: RS232C, some more commands (PRs are welcome)

## Install

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

## Usage
{{usage}}
