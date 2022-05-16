from __future__ import annotations
from typing import Optional, Callable
from DoWhile import do_while_no_return_arg


class Menu:
    def __init__(self,
                 prompt: str,
                 valid_input_checker: Callable,
                 valid_input_args: tuple,
                 action: Callable = None,
                 action_args: tuple = (),
                 main_menu: Optional[Menu] = None,
                 parent_menu: Optional[Menu] = None):
        self.main = main_menu
        if main_menu is None:
            self.main = self
        self.parent = parent_menu
        self.prompt = prompt
        self.checkInput = valid_input_checker
        self.checkArgs = valid_input_args
        self.children: list[Menu] = []
        self.settings: dict[str] = {}
        self.action = action
        self.actionArgs = action_args
        if action is None:
            self.action = self.default_action

    def show_to_user(self, input_on_same_line: bool = True):
        def inner():
            if input_on_same_line:
                user_input = input(self.prompt)
            else:
                print(self.prompt)
                user_input = input()
            return user_input
        args = self.actionArgs + (do_while_no_return_arg(func=inner,
                                                         condition=self.checkInput,
                                                         cond_args=self.checkArgs),)
        self.action(*args)

    def add_child(self, prompt: str,
                  valid_input_checker: Callable,
                  valid_input_args: tuple,
                  action: Callable = None,
                  action_args: tuple = ()):
        child = Menu(prompt, valid_input_checker, valid_input_args, action, action_args, self.main, self)
        self.children.append(child)
        return child

    def default_action(self, user_choice: str):
        if int(user_choice)-1 == len(self.children) and self.parent is not None:
            self.parent.show_to_user()
        elif int(user_choice)-1 < len(self.children):
            self.children[int(user_choice)-1].show_to_user()
