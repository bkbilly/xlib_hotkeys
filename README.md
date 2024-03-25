# xlib-hotkeys

[![pypi](https://img.shields.io/pypi/v/xlib-hotkeys.svg)](https://pypi.python.org/pypi/xlib-hotkeys)
![python version](https://img.shields.io/pypi/pyversions/xlib-hotkeys.svg)
![license](https://img.shields.io/pypi/l/xlib-hotkeys.svg)

Python library for Linux to register keyboard combinations to a callback function.


## Requirements
* Python 3.7 or later


## Installation
Install using:
```
pip install xlib-hotkeys
```


## Usage
You can use this module from the command line
```bash
xlib-hotkeys -h
xlib-hotkeys -d :0 -k ctrl+return shift+f2
```

```python
from xlib_hotkeys import HotKeysManager


def KeyDown(key, keyspressed):
    print(f"Keys Pressed: {keyspressed}")


def Hotkey1():
    print(f" Hotkey1 detected")


def Hotkey2():
    print(f" Hotkey2 detected")


hk = HotKeysManager(display_str=":0")
hk.KeyDown = KeyDown
hk.hotkeys["ctrl+return"] = Hotkey1()
hk.hotkeys["shift+f2"] = Hotkey2()

hk.start()
time.sleep(50)
hk.stop()
```
