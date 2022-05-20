from random import random
from typing import Callable, Optional
from wave import Wave_read
from GroupEntry import GroupEntry
from Option import Option


class Group:
    def __init__(self,
                 name: str,
                 play_randomly: bool,
                 hotkeys: list[str],
                 group_entries: list[GroupEntry]):
        self.name = name
        self.playRandomly = play_randomly
        self.hotkeys = hotkeys
        self.groupEntries = group_entries
        self.weightSum = 0
        for group_entry in group_entries:
            self.weightSum += group_entry.weight
        self.orderTracker = 0

    def play(self, options: dict[str, Option],
             get_current_sound_playing: Callable[[None], Optional[Wave_read]],
             set_current_sound_playing: Callable[[Wave_read], None],
             are_all_sounds_stopped: Callable[[None], bool]):
        if self.playRandomly:
            random_number = random() * self.weightSum
            for group_entry in self.groupEntries:
                if random_number <= group_entry.weight:
                    group_entry.soundEntry.play(options,
                                                get_current_sound_playing,
                                                set_current_sound_playing,
                                                are_all_sounds_stopped)
                    break
                else:
                    random_number -= group_entry.weight
        else:
            sound_in_front_of_line = self.groupEntries[self.orderTracker].soundEntry
            sound_in_front_of_line.play(options,
                                        get_current_sound_playing,
                                        set_current_sound_playing,
                                        are_all_sounds_stopped)
            self.orderTracker += 1
            if self.orderTracker > len(self.groupEntries) - 1:
                self.orderTracker = 0
