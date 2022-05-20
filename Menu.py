from __future__ import annotations
from typing import Optional, Callable
from DoWhile import do_while_no_return_arg


def default_action(menu: Menu, user_choice: str):
    if int(user_choice) - 1 == len(menu.children) and menu.parent is not None:
        menu.parent.show_to_user()
    elif int(user_choice) - 1 < len(menu.children):
        menu.children[int(user_choice) - 1].show_to_user()


class Menu:
    def __init__(self,
                 valid_input_checker: Callable[..., bool],
                 valid_input_args: tuple,
                 prompt_getter: Optional[Callable[..., str]] = None,
                 prompt_args: tuple = (),
                 prompt: Optional[str] = None,
                 action: Callable[..., None] = None,
                 action_args: tuple = (),
                 main_menu: Optional[Menu] = None,
                 parent_menu: Optional[Menu] = None):
        self.main = main_menu
        if main_menu is None:
            self.main = self
        self.parent = parent_menu
        self.prompt = prompt
        self.prompt_getter = prompt_getter
        self.promptArgs = prompt_args
        self.checkInput = valid_input_checker
        self.checkArgs = valid_input_args
        self.children: list[Menu] = []
        self.settings: dict[str] = {}
        self.action = action
        self.actionArgs = action_args
        if action is None:
            self.action = default_action

    def show_to_user(self, input_on_same_line: bool = True):
        prompt = ""
        if self.prompt is None and self.prompt_getter is None:
            prompt = "This menu does not have a prompt!"
        elif self.prompt is not None:
            prompt = self.prompt
        else:
            prompt = self.prompt_getter(*self.promptArgs)

        def inner():
            if input_on_same_line:
                user_input = input(prompt)
            else:
                print(prompt)
                user_input = input()
            return user_input
        args = (self,)
        args += (do_while_no_return_arg(func=inner,
                                        condition=self.checkInput,
                                        cond_args=self.checkArgs),)
        args += self.actionArgs
        self.action(*args)

    def add_child(self,
                  valid_input_checker: Callable[..., bool],
                  valid_input_args: tuple,
                  prompt_getter: Optional[Callable[..., str]] = None,
                  prompt_args: tuple = (),
                  prompt: Optional[str] = None,
                  action: Callable[..., None] = None,
                  action_args: tuple = ()):
        child = Menu(valid_input_checker, valid_input_args, prompt_getter,
                     prompt_args, prompt, action, action_args, self.main, self)
        self.children.append(child)
        return child
