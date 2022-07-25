import tkinter as tk
import tkinter.ttk as ttk
from threading import Thread

from Hotkey import Hotkey


class GUIHotkey:
    def __init__(self, root, master=None, gui_group=None, hotkey=None, button_deletes=True):
        self.root = root
        self.guiGroup = gui_group
        self.master = master if (gui_group is None) else gui_group.frm_hotkeys
        self.tmp_hk = None
        self.hotkey = hotkey
        self.frm = ttk.Frame(master=self.master)
        self.name = tk.StringVar(value="No hotkey")
        if hotkey is not None:
            self.name.set(hotkey.name)
        self.events = []
        lbl = ttk.Label(self.frm,
                        textvariable=self.name,
                        justify="left")
        if button_deletes:
            btn_del_refresh = ttk.Button(self.frm,
                                         image=root.icons["trash"],
                                         width=1,
                                         command=self.delete)
        else:
            btn_del_refresh = ttk.Button(self.frm,
                                         image=root.icons["refresh"],
                                         width=1,
                                         command=self.start_detect)

        btn_del_refresh.pack(side="right")
        lbl.pack(side="left", fill="x")
        self.frm.pack(fill="x", side="top")

    def delete(self):
        if self.hotkey is not None and self.hotkey.detecting:
            return
        self.root.hotkeysToDelete.append(self)
        self.root.window.event_generate("<<DeleteHotkeys>>")

    def update(self, hotkey):
        self.hotkey = hotkey
        self.name.set(hotkey.name)

    def start_detect(self):
        if self.root.detectingHotkey is not None:
            return
        self.name.set("Detecting...")
        self.root.detectingHotkey = self
        self.tmp_hk = Hotkey()
        finishDetectThread = Thread(target=self.finish_detect)
        finishDetectThread.start()

    def finish_detect(self):
        self.tmp_hk.detect()
        poll = self.root.soundboard.options["Poll For Keyboard"].state
        if self.guiGroup is not None:
            hk = self.guiGroup.group.add_hotkey(self.tmp_hk.name, self.tmp_hk.keys)
            if hk is not None:
                self.update(hk)
                if not poll:
                    self.guiGroup.group.hook_all_hotkeys()
            else:
                self.delete()
        elif not self.root.soundboard.hotkey_exists(self.tmp_hk.keys):
            self.hotkey.name, self.hotkey.keys = self.tmp_hk.name, self.tmp_hk.keys
            if not poll:
                self.hotkey.update_hook()
            self.name.set(self.hotkey.name)
        else:
            self.name.set(self.hotkey.name)
        self.root.detectingHotkey = None
