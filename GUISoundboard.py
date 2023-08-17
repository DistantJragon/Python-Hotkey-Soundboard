import tkinter as tk
import tkinter.ttk as ttk

from ScrollableFrame import ScrollableFrame
from tkinterdnd2 import *

from GUIGroup import GUIGroup
from GUIHotkey import GUIHotkey
from GUIOption import GUIOption


class GUISoundboard:
    def __init__(self, s):
        self.soundboard = s
        self.selectedEntry = None
        self.entriesToUpdate = []
        self.groupsToUpdate = []
        self.groupsToDelete = []
        self.groupsToRemove = []
        self.groupsToRename = []
        self.groupHotkeysToUpdate = []
        self.hotkeysToDelete = []
        self.detectingHotkey = None
        self.conflictingGroups = []
        self.window = TkinterDnD.Tk()
        self.window.title("Python Hotkey Soundboard")
        self.ttk_styling = ttk.Style()
        self.ttk_styling.configure("GreyedOut.TCheckbutton", foreground="#603030")
        self.ttk_styling.configure("Selected.TFrame", relief="raised")
        self.ttk_styling.configure("Red.TLabel", foreground="red")
        self.ttk_styling.configure("Red.TEntry", foreground="red")
        self.window.geometry("1080x720")
        self.window.bind("<Escape>", self.remove_selection)
        self.window.bind("<<DeleteGroup>>", self.delete_group)
        self.window.bind("<<DeleteGroupName>>", self.delete_group_from_cbx)
        self.window.bind("<<RemoveGroup>>", self.remove_group_from_editor)
        self.window.bind("<<UpdateGroup>>", self.update_group_entries)
        self.window.bind("<<UpdateEntry>>", self.update_entry)
        self.window.bind("<<RenameGroup>>", self.rename_group)
        self.window.bind("<<UpdateHotkeys>>", self.update_hotkeys)
        self.window.bind("<<DeleteHotkeys>>", self.delete_hotkeys)
        self.window.bind("<Up>", self.swap_entry_up)
        self.window.bind("<Down>", self.swap_entry_down)
        frm_main = ttk.Frame(self.window)
        self.options_and_chooser = ttk.Frame(frm_main)
        self.options_and_chooser.pack(side="left")
        self.frm_group_chooser = ttk.Frame(self.options_and_chooser, padding=20)
        group_names = [g.name for g in s.groupList]
        self.cbx_group_chooser = ttk.Combobox(self.frm_group_chooser,
                                              values=group_names)
        self.cbx_group_chooser.current(0)
        self.cbx_group_chooser.pack(side="left")
        self.cbx_group_chooser.bind("<Return>", lambda e: self.add_group_to_editor())
        self.icons = {"trash": tk.PhotoImage(file="Program Images/trash icon.png"),
                      "back": tk.PhotoImage(file="Program Images/arrow back.png"),
                      "refresh": tk.PhotoImage(file="Program Images/refresh.png")}
        self.group_widgets = []

        btn_add_group = ttk.Button(self.frm_group_chooser,
                                   text="+",
                                   width=1,
                                   command=self.add_group_to_editor)
        btn_add_group.pack(side="left")
        btn_delete_group = ttk.Button(self.frm_group_chooser,
                                      image=self.icons["trash"],
                                      width=1)
        btn_delete_group.bind("<Double-Button-1>",
                              lambda e: self.window.event_generate("<<DeleteGroupName>>", when="tail"))
        btn_delete_group.pack(side="left")
        self.options = {}
        self.frm_group_chooser.pack(side="top")
        for name, option in s.options.items():
            if name == "Device":
                continue
            self.options[name] = GUIOption(self, option)
        devices = ["Default", *list(s.devices.values())]
        self.options["Device Name"].value = tk.StringVar(value=s.options["Device Name"].state)
        self.options["Device Name"].ui = ttk.Combobox(master=self.options["Device Name"].frm,
                                                      values=devices,
                                                      state="readonly",
                                                      textvariable=self.options["Device Name"].value)
        self.options["Device Name"].lbl["text"] = "Device"
        self.options["Poll For Keyboard"].value = tk.BooleanVar(value=s.options["Poll For Keyboard"].state)
        self.options["Poll For Keyboard"].ui = ttk.Checkbutton(master=self.options["Poll For Keyboard"].frm,
                                                               variable=self.options["Poll For Keyboard"].value,
                                                               onvalue=True, offvalue=False)
        self.options["Polling Rate"].value = tk.DoubleVar(value=s.options["Polling Rate"].state)
        self.options["Polling Rate"].ui = ttk.Spinbox(master=self.options["Polling Rate"].frm,
                                                      textvariable=self.options["Polling Rate"].value,
                                                      width=5,
                                                      from_=0,
                                                      to=1,
                                                      increment=0.01)
        self.options["\"Stop All Sounds\" Hotkey"].ui = GUIHotkey(root=self,
                                                                  master=self.options["\"Stop All Sounds\" Hotkey"].frm,
                                                                  hotkey=self.soundboard.stopAllSoundsHotkey,
                                                                  button_deletes=False).frm
        self.options["Stop All Sounds With New Sound"].value = tk.BooleanVar(
            value=s.options["Stop All Sounds With New Sound"].state)
        self.options["Stop All Sounds With New Sound"].ui = ttk.Checkbutton(
            master=self.options["Stop All Sounds With New Sound"].frm,
            variable=self.options["Stop All Sounds With New Sound"].value,
            onvalue=True, offvalue=False)
        self.options["Number Of Streams"].value = tk.IntVar(value=s.options["Number Of Streams"].state)
        self.options["Number Of Streams"].ui = ttk.Spinbox(master=self.options["Number Of Streams"].frm,
                                                           textvariable=self.options["Number Of Streams"].value,
                                                           width=3,
                                                           from_=0,
                                                           to=99,
                                                           increment=1)
        self.options["Delay Before New Sound Can Play"].value = tk.DoubleVar(
            value=s.options["Delay Before New Sound Can Play"].state)
        self.options["Delay Before New Sound Can Play"].ui = ttk.Spinbox(
            master=self.options["Delay Before New Sound Can Play"].frm,
            textvariable=self.options["Delay Before New Sound Can Play"].value,
            width=7,
            from_=0,
            to=100,
            increment=0.01)
        self.options["Chunk Size"].value = tk.IntVar(
            value=s.options["Chunk Size"].state)
        self.options["Chunk Size"].ui = ttk.Spinbox(
            master=self.options["Chunk Size"].frm,
            textvariable=self.options["Chunk Size"].value,
            width=5,
            from_=0,
            to=9999,
            increment=1)
        for option in self.options.values():
            if option.ui is not None:
                option.ui.pack(side="right")
            option.add_trace_to_value()
        self.btn_save_var = tk.StringVar(value="Save")
        btn_save_options = ttk.Button(master=self.options_and_chooser,
                                      textvariable=self.btn_save_var,
                                      command=self.save)
        btn_save_options.pack()
        separator = ttk.Separator(master=frm_main, orient='vertical')
        separator.pack(side="left", fill='y')
        scr_frm_groups = ScrollableFrame(frm_main)
        self.frm_groups = scr_frm_groups.scrollable_frame
        for group in s.groupList:
            self.make_group_widget(sb_group=group)
        scr_frm_groups.pack(fill="both", side="right", expand=True)
        frm_main.pack(fill="both", expand=True)

    def save(self):
        self.btn_save_var.set("Saving...")
        for name, option in self.options.items():
            if name != "\"Stop All Sounds\" Hotkey":
                option.update()
                option.set_lbl()
        self.soundboard.save_options()
        self.soundboard.restart()
        self.options["Device Name"].ui.set(self.soundboard.options["Device Name"].state)
        self.btn_save_var.set("Save")

    def make_group_widget(self,
                          sb_group=None,
                          group_name=None):
        if sb_group is not None or group_name is not None:
            self.group_widgets.append(GUIGroup(self,
                                               sb_group,
                                               group_name))
        else:
            raise ValueError("No group name or id given")
        return self.group_widgets[-1]

    def add_group_name_to_group_chooser(self, group_name):
        cbx_values = list(self.cbx_group_chooser["values"])
        if group_name not in cbx_values:
            cbx_values.append(group_name)
            self.cbx_group_chooser["values"] = cbx_values
            if self.cbx_group_chooser.get() == "":
                self.cbx_group_chooser.current(0)

    def remove_group_name_from_group_chooser(self, group_name):
        cbx_values = list(self.cbx_group_chooser["values"])
        if group_name in cbx_values:
            cbx_values.remove(group_name)
            self.cbx_group_chooser["values"] = cbx_values
        if self.cbx_group_chooser.get() == group_name:
            self.cbx_group_chooser.set("")
            if len(cbx_values) > 0:
                self.cbx_group_chooser.current(0)

    def delete_group(self, _):
        gui_group = self.groupsToDelete[0]
        self.soundboard.delete_group(gui_group.group)
        gui_group.frame.destroy()
        self.group_widgets.remove(gui_group)
        self.groupsToDelete.pop(0)

    def delete_group_from_cbx(self, _):
        group_name = self.cbx_group_chooser.get()
        for gui_group in self.group_widgets:
            if group_name == gui_group.name.get():
                gui_group.queue_delete()
        self.remove_group_name_from_group_chooser(group_name)

    def add_group_to_editor(self):
        group_name = self.cbx_group_chooser.get()
        if group_name != "":
            group_names = [x.name.get() for x in self.group_widgets]
            if group_name not in group_names:
                group = self.make_group_widget(group_name=group_name)
            else:
                group = [x for x in self.group_widgets if x.name.get() == group_name][0]
            if not group.isPacked:
                group.frame.pack(fill="x", pady=10)
                group.frame.drop_target_register(DND_FILES)
                group.frame.dnd_bind("<<Drop:DND_Files>>", group.file_dropped)
            group.isPacked = True
        self.remove_group_name_from_group_chooser(group_name)

    def remove_group_from_editor(self, _):
        group = self.groupsToRemove[0]
        group_name = group.name.get()
        cbx_values = list(self.cbx_group_chooser["values"])
        cbx_values.append(group_name)
        self.cbx_group_chooser["values"] = cbx_values
        if self.cbx_group_chooser.get() == "":
            self.cbx_group_chooser.current(0)
        group.frame.pack_forget()
        group.frame.drop_target_unregister()
        group.isPacked = False
        self.groupsToRemove.pop(0)

    def remove_selection(self, _):
        if self.selectedEntry is not None:
            self.selectedEntry.frm["style"] = "TFrame"
        self.selectedEntry = None

    def update_group_entries(self, _):
        self.groupsToUpdate[0].update_entries()
        self.groupsToUpdate.pop(0)

    def update_entry(self, _):
        guiE = self.entriesToUpdate[0]
        try:
            w = guiE.weight.get()
        except tk.TclError:
            w = 0
        guiE.entry.weight = w
        self.entriesToUpdate.pop(0)

    def update_hotkeys(self, _):
        self.groupHotkeysToUpdate[0].update_hotkeys()
        self.groupHotkeysToUpdate.pop(0)

    def delete_hotkeys(self, _):
        hotkey = self.hotkeysToDelete[-1]
        if hotkey.hotkey is not None:
            hotkey.guiGroup.group.remove_hotkey(hotkey.hotkey)
        hotkey.frm.destroy()
        hotkey.guiGroup.hotkeys.remove(hotkey)

    def rename_group(self, _):
        gui_group = self.groupsToRename[0]
        gui_group.group.name = gui_group.name.get()
        name_list = {}
        for gui_group in self.group_widgets:
            if gui_group.name.get() in name_list.keys():
                name_list[gui_group.name.get()].entry_group_name["style"] = "Red.TEntry"
                gui_group.entry_group_name["style"] = "Red.TEntry"
            else:
                gui_group.entry_group_name["style"] = "TEntry"
                name_list[gui_group.name.get()] = gui_group
        self.groupsToRename.pop(0)

    def update_options(self, _):
        pass

    def swap_entry_up(self, _):
        if self.selectedEntry is None:
            return
        guiG = self.selectedEntry.guiGroup
        g = guiG.group
        e = self.selectedEntry.index
        if e > 0:
            g.swap_up(e)
            self.selectedEntry = guiG.entries[e - 1]
            guiG.queue_update_entries()

    def swap_entry_down(self, _):
        if self.selectedEntry is None:
            return
        guiG = self.selectedEntry.guiGroup
        g = guiG.group
        e = self.selectedEntry.index
        if e < len(guiG.entries) - 1:
            g.swap_down(e)
            self.selectedEntry = guiG.entries[e + 1]
            guiG.queue_update_entries()


def max_plus_one(given_list):
    if len(given_list) == 0:
        return 0
    return max(given_list) + 1
