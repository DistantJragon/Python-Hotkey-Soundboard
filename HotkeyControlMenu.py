from typing import Callable, Optional

from BaseMenu import BaseMenu
from MenuICPG import MenuICPG
import time
import keyboard


class HotkeyControlMenuICPG(BaseMenu):
    def __init__(self,
                 prompt: Optional[str] = None,
                 action: Callable[..., None] = None,
                 action_args: tuple = (),
                 main_menu: Optional[MenuICPG] = None,
                 parent_menu: Optional[MenuICPG] = None):
        super().__init__(prompt,
                         main_menu,
                         parent_menu)
        self.events: list[keyboard.KeyboardEvent] = []
        self.action = action
        self.actionArgs = action_args

    def show_to_user(self, input_on_same_line: bool = True):
        if self.prompt is None:
            prompt = "This menu does not have a prompt!"
        else:
            prompt = self.prompt

        callback = keyboard.hook(callback=self.check_and_add_event)
        print(prompt)
        keyboard.read_event()
        time.sleep(0.25)
        keyboard.unhook(callback)
        self.action(self, self.events, *self.actionArgs)

    def check_and_add_event(self, event: keyboard.KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN:
            self.events.append(event)

