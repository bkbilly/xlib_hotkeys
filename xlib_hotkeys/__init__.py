import sys
import time
import threading

import Xlib.X
import Xlib.XK
import Xlib.display
import Xlib.keysymdef
import Xlib.ext.record
import Xlib.protocol.rq


class TimedSet(set):
    def __init__(self, keytimeout):
        self.__table = {}
        self.keytimeout = keytimeout

    def add(self, item):
        self.__table[item] = time.time() + self.keytimeout
        set.add(self, item)

    def __contains__(self, item):
        return time.time() < self.__table.get(item)

    def __iter__(self):
        for item in set.__iter__(self):
            if time.time() < self.__table.get(item):
                yield item


class HotKeysManager(threading.Thread):

    def __init__(self, display_str=None, keytimeout=3):
        threading.Thread.__init__(self, daemon=True)
        self.finished = threading.Event()

        # Give these some initial values
        self.activekeys = TimedSet(keytimeout)
        self.hotkeys = {}

        # Load missing keys
        for group in Xlib.keysymdef.__all__:
            Xlib.XK.load_keysym_group(group)

        # Assign default function actions (do nothing).
        self.KeyDown = lambda x, y: True

        self.contextEventMask = [Xlib.X.KeyPress, Xlib.X.KeyRelease]
        # Hook to our display.
        self.local_dpy = Xlib.display.Display(display_str)
        self.record_dpy = Xlib.display.Display(display_str)

    def run(self):
        # Check if the extension is present
        if not self.record_dpy.has_extension("RECORD"):
            sys.exit(1)

        self.ctx = self.record_dpy.record_create_context(
            0,
            [Xlib.ext.record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': tuple(self.contextEventMask),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])

        # Enable the context; this only returns after a call to record_disable_context,
        # while calling the callback function in the meantime
        self.record_dpy.record_enable_context(self.ctx, self.processevents)
        # Finally free the context
        self.record_dpy.record_free_context(self.ctx)

    def stop(self):
        self.finished.set()
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()

    def processevents(self, reply):
        if reply.category != Xlib.ext.record.FromServer:
            return
        if reply.client_swapped:
            return
        data = reply.data
        while len(data):
            event, data = Xlib.protocol.rq.EventField(None).parse_binary_value(
                data, self.local_dpy.display, None, None)
            if event.type == Xlib.X.KeyPress:
                self.keypressevent(event)
            elif event.type == Xlib.X.KeyRelease:
                self.keyreleaseevent(event)

    def hotkey_check(self):
        for hotkey, callback in self.hotkeys.items():
            hotkey = hotkey.replace("<", "")
            hotkey = hotkey.replace(">", "")
            if set(hotkey.split("+")).issubset(self.activekeys):
                callback()

    def keypressevent(self, event):
        key = self.lookup_keysym(event)
        self.activekeys.add(key)
        keyspressed = "+".join(sorted(self.activekeys, key=len, reverse=True))
        self.KeyDown(key, keyspressed)
        self.hotkey_check()

    def keyreleaseevent(self, event):
        self.activekeys.discard(self.lookup_keysym(event))

    def lookup_keysym(self, event):
        keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        for name in dir(Xlib.XK):
            if name.startswith("XK_") and getattr(Xlib.XK, name) == keysym:
                name = name.removeprefix("XK_")
                name = name.removeprefix("XF86_")
                name = name.removeprefix("Audio")
                name = name.removesuffix("_L")
                name = name.removesuffix("_R")
                name = name.replace("Control", "ctrl")
                name = name.lower()
                return name
        return str(event.detail)
