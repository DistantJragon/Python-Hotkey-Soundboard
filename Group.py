from random import random
from typing import Callable, Optional
from wave import Wave_read
from Entry import Entry
from Option import Option


class Group:
    def __init__(self,
                 name: str,
                 play_randomly: bool,
                 hotkeys: list[str],
                 sound_entries_weights: dict[Entry, int]):
        self.name = name
        self.playRandomly = play_randomly
        self.hotkeys = hotkeys
        self.soundEntryWeights = sound_entries_weights
        self.weightSum = 0
        for key in sound_entries_weights:
            self.weightSum += sound_entries_weights[key]
        self.orderTracker = 0

    def play(self, options: dict[str, Option],
             get_current_sound_playing: Callable[[], Optional[Wave_read]],
             set_current_sound_playing: Callable[[Wave_read], None]):
        sound_entry_list = [e for e in self.soundEntryWeights]
        if self.playRandomly:
            random_number = random() * self.weightSum
            for current_sound in sound_entry_list:
                if random_number <= self.soundEntryWeights[current_sound]:
                    current_sound.play(options,
                                       get_current_sound_playing,
                                       set_current_sound_playing)
                    break
                else:
                    random_number -= self.soundEntryWeights[current_sound]
        else:
            sound_in_front_of_line = sound_entry_list[self.orderTracker]
            sound_in_front_of_line.play(options,
                                        get_current_sound_playing,
                                        set_current_sound_playing)
            self.orderTracker += 1
            if self.orderTracker > len(sound_entry_list) - 1:
                self.orderTracker = 0
