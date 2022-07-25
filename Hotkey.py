from threading import Thread
from time import sleep

from keyboard import add_hotkey, remove_hotkey, hook, KEY_DOWN, read_event, unhook, KeyboardEvent


class Hotkey:
    def __init__(self, name=None, keys=None):
        self.name = name
        self.keys = keys
        self.callback = None
        self.last_func = None
        self.last_timeout = None
        self.events = []
        self.detecting = False

    def hook(self, func, timeout):
        if self.callback is None:
            self.last_func, self.last_timeout = func, timeout
            # Need lambda so different hotkeys with same funcs have
            # "different" callbacks to prevent errors when unhooking
            self.callback = add_hotkey(hotkey=tuple(self.keys),
                                       callback=lambda: func(),
                                       timeout=timeout)

    def unhook(self):
        if self.callback is not None:
            remove_hotkey(self.callback)
            self.callback = None

    def update_hook(self):
        self.unhook()
        if self.last_func is None or self.last_timeout is None:
            raise TypeError("Arguments can't be none")
        self.hook(self.last_func, self.last_timeout)

    def update_all(self, name, keys):
        self.name, self.keys = name, keys
        if self.last_func is not None and self.last_timeout is not None:
            self.update_hook()

    def detect(self):
        self.unhook()
        self.events.clear()
        callback = hook(callback=self.check_and_add_event)
        read_event()
        sleep(0.5)
        unhook(callback)
        self.detecting = False
        name = ""
        keys = []
        for e in self.events:
            name += e.name + "+"
            keys.append(e.scan_code)
        name = name[:-1]
        self.name, self.keys = name, keys

    def async_detect(self):
        detectThread = Thread(target=self.detect)
        detectThread.start()

    def check_and_add_event(self, event):
        if event.event_type == KEY_DOWN:
            self.events.append(event)
