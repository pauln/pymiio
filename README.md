# pymiio
Interact with Xiaomi Smart Home (Mijia) devices using Python

## Status
This project is still under development.  As such, anything and everything could change at any time.

## Usage
Two scripts are currently provided as both utilities and examples: `discover.py` searches for miIO-compatible devices on your network, printing out various parameters of each device it finds; if you have a Lumi gateway, `listen.py` will attempt to find it and connect to its multicast stream, reporting anything other than gateway heartbeats.

As noted above, `pymiio` is still under development - so these scripts should be considered unfinished and potentially unstable; they are also likely to change at a high rate due to being used as part of the development process.
