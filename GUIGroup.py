import tkinter as tk
import tkinter.ttk as ttk
from os.path import isdir

from GUIEntry import GUIEntry
from GUIHotkey import GUIHotkey
from Group import Group


class GUIGroup:
    def __init__(self, root, group=None, group_name=None):
        self.root = root
        trash = root.icons["trash"]
        back_arrow = root.icons["back"]
        if group is not None:
            self.group = group
            self.name = tk.StringVar(value=group.name)
            self.playsRandomly = tk.BooleanVar(value=group.playRandomly)
        elif group_name is not None:
            sb = root.soundboard
            self.group = Group(sb, group_name)
            sb.groupList.append(self.group)
            self.name = tk.StringVar(value=group_name)
            self.playsRandomly = tk.BooleanVar(value=True)
        else:
            raise ValueError("No group or group_name given")
        self.isPacked = False
        self.isConflicting = False

        self.frame = ttk.Frame(master=root.frm_groups, padding=10, relief="ridge", borderwidth=2)

        frm_group_info = ttk.Frame(master=self.frame)
        self.entry_group_name = ttk.Entry(frm_group_info,
                                          textvariable=self.name,
                                          justify="center")
        self.entry_group_name.pack(side="left", fill="x", expand=True)

        self.name.trace_add("write", lambda *_: self.queue_rename())

        btn_delete_group = ttk.Button(master=frm_group_info,
                                      image=trash)
        btn_delete_group.bind("<Double-Button-1>", lambda e: self.queue_delete())

        btn_remove_group = ttk.Button(master=frm_group_info,
                                      image=back_arrow,
                                      command=self.queue_remove)
        btn_delete_group.pack(side="right")
        btn_remove_group.pack(side="right")
        frm_group_info.pack(fill="x")

        self.cbt_play_style = ttk.Checkbutton(master=self.frame,
                                              text="Plays Randomly",
                                              variable=self.playsRandomly,
                                              command=self.change_play_style,
                                              onvalue=True, offvalue=False)
        self.change_play_style()
        self.cbt_play_style.pack(side="top")
        self.frm_group_main = ttk.Frame(master=self.frame)
        self.frm_entries = tk.Frame(master=self.frm_group_main, relief="sunken", borderwidth=2)
        self.frm_entries.pack(fill="both", expand=True, side="left", padx=5)
        self.frm_hotkeys = ttk.Frame(master=self.frm_group_main, relief="sunken", borderwidth=2)
        self.frm_hotkeys.pack(fill="both", expand=True, side="left", padx=5)
        self.entries = []
        self.hotkeys = []
        self.queue_update_entries()
        self.queue_update_hotkeys()
        btn_add_hotkey = ttk.Button(master=self.frm_hotkeys, text="+", command=self.add_hotkey)
        btn_add_hotkey.pack(side="bottom")
        self.frm_group_main.pack(fill="x", side="left", expand=True)

    def update_entries(self):
        lenGE = len(self.group.groupEntries)
        lenE = len(self.entries)
        for i in range(lenGE):
            entry = self.group.groupEntries[i]
            if i >= lenE:
                self.entries.append(GUIEntry(self, entry, i))
                continue
            self.entries[i].update(entry)
        if lenGE < lenE:
            for i in range(lenGE, lenE):
                self.entries[i].frm.destroy()
            self.entries = self.entries[:lenGE]

    def update_hotkeys(self):
        lenGH = len(self.group.hotkeys)
        lenH = len(self.hotkeys)
        for i in range(lenGH):
            hotkey = self.group.hotkeys[i]
            if i >= lenH:
                self.hotkeys.append(GUIHotkey(root=self.root, gui_group=self, hotkey=hotkey))
                continue
            self.hotkeys[i].update(hotkey)
        # Doesn't work b/c of GUIHotkeys being detected
        # if lenGH < lenH:
        #     for i in range(lenGH, lenH):
        #         self.hotkeys[i].frm.destroy()
        #     self.hotkeys = self.hotkeys[:lenGH]

    def queue_delete(self):
        self.root.groupsToDelete.append(self)
        self.root.window.event_generate("<<DeleteGroup>>", when="tail")

    def queue_remove(self):
        if self.name.get() == "":
            return
        self.root.groupsToRemove.append(self)
        self.root.window.event_generate("<<RemoveGroup>>", when="tail")

    def queue_update_entries(self):
        self.root.groupsToUpdate.append(self)
        self.root.window.event_generate("<<UpdateGroup>>", when="tail")

    def queue_update_hotkeys(self):
        self.root.groupHotkeysToUpdate.append(self)
        self.root.window.event_generate("<<UpdateHotkeys>>", when="tail")

    def queue_rename(self):
        self.root.groupsToRename.append(self)
        self.root.window.event_generate("<<RenameGroup>>", when="tail")

    def change_play_style(self):
        self.group.playRandomly = self.playsRandomly.get()
        if self.playsRandomly.get():
            self.cbt_play_style["style"] = "TCheckbutton"
        else:
            self.cbt_play_style["style"] = "GreyedOut.TCheckbutton"

    def add_hotkey(self):
        if self.root.detectingHotkey is not None:
            return
        self.hotkeys.append(GUIHotkey(root=self.root, gui_group=self))
        self.hotkeys[-1].start_detect()
        self.queue_update_hotkeys()

    def file_dropped(self, e):
        files = self.frame.tk.splitlist(e.data)
        for file in files:
            if len(file) >= 4 and file[-4:] == ".wav":
                self.group.add_group_entry(file, 1)
            elif isdir(file):
                self.group.add_directory(file, 1)
        self.queue_update_entries()
