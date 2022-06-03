from __future__ import annotations
from typing import Optional, Callable
from BaseMenu import BaseMenu
from MenuIC import MenuIC, default_action
from DoWhile import do_while_no_return_arg


class MenuICPG(MenuIC):
    def __init__(self,
                 valid_input_checker: Callable[..., bool],
                 valid_input_args: tuple,
                 prompt_getter: Optional[Callable[..., str]] = None,
                 prompt_args: tuple = (),
                 prompt: Optional[str] = None,
                 action: Callable[..., None] = default_action,
                 action_args: tuple = (),
                 main_menu: Optional[BaseMenu] = None,
                 parent_menu: Optional[BaseMenu] = None):
        super().__init__(valid_input_checker, valid_input_args, prompt, action, action_args, main_menu, parent_menu)
        self.prompt_getter = prompt_getter
        self.promptArgs = prompt_args

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

        if self.action is default_action and len(self.checkArgs) == 0:
            cond_args = (1, len(self.children))
        else:
            cond_args = self.checkArgs

        self.action(self,
                    do_while_no_return_arg(func=inner,
                                           condition=self.checkInput,
                                           cond_args=cond_args),
                    *self.actionArgs)
