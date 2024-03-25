import time
import argparse
from . import HotKeysManager


def KeyDown(key, keyspressed):
    print(f"Keys Pressed: {keyspressed}")


def Hotkey(hotkey):
    print(f" Hotkey detected: {hotkey}")


def main():
    parser = argparse.ArgumentParser(
        prog="xlib-hotkeys",
        description="Register Hotkeys")
    parser.add_argument("-d", "--display", default=None, help="Setup display")
    parser.add_argument("-k", "--key", nargs="*", help="Register hotkeys")
    args = parser.parse_args()

    hk = HotKeysManager(args.display)
    hk.KeyDown = KeyDown

    if args.key is not None:
        for key in args.key:
            hk.hotkeys[key] = lambda key=key: Hotkey(key)

    hk.start()
    time.sleep(50)
    hk.stop()
