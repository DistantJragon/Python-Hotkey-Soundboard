from __future__ import annotations
from typing import Optional


class BaseMenu:
    def __init__(self,
                 prompt: Optional[str] = None,
                 main_menu: Optional[BaseMenu] = None,
                 parent_menu: Optional[BaseMenu] = None):
        self.main = main_menu
        if main_menu is None:
            self.main = self
        self.parent = parent_menu
        self.prompt = prompt
        self.children: list[BaseMenu] = []

    def show_to_user(self):
        raise NotImplementedError("This method must be implemented by a subclass!")

    def add_child(self, menu: BaseMenu):
        self.children.append(menu)
        menu.parent = self
        menu.main = self.main
        menu.set_children_main()

    def set_children_main(self):
        for child in self.children:
            child.main = self.main
            child.set_children_main()

