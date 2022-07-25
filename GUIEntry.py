import tkinter as tk
import tkinter.ttk as ttk

from CreateToolTip import CreateToolTip

from SoundDirectory import SoundDirectory


class GUIEntry:
    def __init__(self, parent, entry, index):
        self.guiGroup = parent
        self.index = index
        self.entry = entry
        self.frm = ttk.Frame(master=self.guiGroup.frm_entries)
        self.name = tk.StringVar(value=entry.name)
        path = entry.filePath
        if type(entry) is SoundDirectory:
            path += "\n" + str(len(entry.entryList)) + " Files"
        self.path = tk.StringVar(value=path)
        self.weight = tk.DoubleVar(value=entry.weight)
        lbl = ttk.Label(self.frm,
                        textvariable=self.name,
                        justify="left")
        lbl.bind("<Button-1>", self.select)
        self.toolTip = CreateToolTip(lbl, self.path)
        self.toolTip.waitTime = 1000
        frm_space = ttk.Frame(master=self.frm, width=20)
        lbl_weight = ttk.Label(self.frm, text="Weight: ")
        spin_weight = ttk.Spinbox(self.frm,
                                  width=5,
                                  textvariable=self.weight,
                                  from_=0,
                                  to=9999)
        self.weight.trace_add("write", self.weight_changed)
        spin_weight.bind("<Button-1>", parent.root.remove_selection)
        trash = self.guiGroup.root.icons["trash"]
        btn_delete_entry = ttk.Button(self.frm,
                                      image=trash,
                                      width=1)
        btn_delete_entry.bind("<Double-Button-1>", self.delete)

        btn_delete_entry.pack(side="right")
        spin_weight.pack(side="right")
        lbl_weight.pack(side="right")
        lbl.pack(side="left", fill="x", expand=True)
        frm_space.pack(side="left")
        self.frm.pack(fill="x")
        if not entry.exists:
            lbl["style"] = "Red.TLabel"
            spin_weight["state"] = "readonly"
            spin_weight["increment"] = 0

    def select(self, _):
        root = self.guiGroup.root
        if root.selectedEntry is not None:
            root.selectedEntry.frm["style"] = "TFrame"
        self.frm["style"] = "Selected.TFrame"
        root.selectedGroup = self.guiGroup
        root.selectedEntry = self
        self.guiGroup.root.window.focus()

    def weight_changed(self, *_):
        root = self.guiGroup.root
        root.entriesToUpdate.append(self)
        root.window.event_generate("<<UpdateEntry>>", when="tail")

    def delete(self, _):
        self.guiGroup.group.groupEntries.remove(self.entry)
        self.guiGroup.queue_update_entries()

    def update(self, entry):
        self.entry = entry
        path = entry.filePath
        if type(entry) is SoundDirectory:
            path += "\n" + str(len(entry.entryList)) + " Files"
        self.name.set(entry.name)
        self.path.set(path)
        self.weight.set(int(entry.weight))
        if self is self.guiGroup.root.selectedEntry:
            self.select(0)
        else:
            self.frm["style"] = "TFrame"
