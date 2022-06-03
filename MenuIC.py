from __future__ import annotations
from typing import Optional, Callable

from BaseMenu import BaseMenu
from DoWhile import do_while_no_return_arg


def default_action(menu: MenuIC, user_choice: str):
    if int(user_choice) - 1 == len(menu.children) and menu.parent is not None:
        menu.parent.show_to_user()
    elif int(user_choice) - 1 < len(menu.children):
        menu.children[int(user_choice) - 1].show_to_user()


def is_int_in_range(min_range: Optional[int], max_range: Optional[int], test: str):
    try:
        test_int = int(test)
    except ValueError:
        return False
    if min_range is not None and min_range > test_int:
        return False
    if max_range is not None and max_range < test_int:
        return False
    return True


def is_not_int_in_range(min_range: Optional[int], max_range: Optional[int], test: str):
    return not is_int_in_range(min_range, max_range, test)


class MenuIC(BaseMenu):
    def __init__(self,
                 valid_input_checker: Callable[..., bool] = is_not_int_in_range,
                 valid_input_args: tuple = (),
                 prompt: Optional[str] = None,
                 action: Callable[..., None] = default_action,
                 action_args: tuple = (),
                 main_menu: Optional[BaseMenu] = None,
                 parent_menu: Optional[BaseMenu] = None):
        super().__init__(prompt,
                         main_menu,
                         parent_menu)
        self.checkInput = valid_input_checker
        self.checkArgs = valid_input_args
        self.children: list[BaseMenu] = []
        self.action = action
        self.actionArgs = action_args

    def show_to_user(self, input_on_same_line: bool = True):
        prompt = ""
        if self.prompt is None:
            prompt = "This menu does not have a prompt!"
        else:
            prompt = self.prompt

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
