import tkinter as tk
import tkinter.ttk as ttk

from CreateToolTip import CreateToolTip


class GUIOption:
    def __init__(self, root, option):
        self.root = root
        self.option = option
        self.value = None
        self.description = tk.StringVar(value=option.description)
        self.frm = ttk.Frame(master=self.root.options_and_chooser)
        self.lbl = ttk.Label(master=self.frm, text=self.option.name, justify="left")
        frm_space = ttk.Frame(master=self.frm, width=20)
        self.toolTip = CreateToolTip(self.lbl, self.description)
        self.toolTip.waitTime = 1000
        self.ui = None
        self.lbl.pack(side="left")
        frm_space.pack(side="left")
        self.frm.pack(fill="x", padx=10, pady=2)

    def update(self):
        if self.value is not None:
            self.option.state = self.value.get()