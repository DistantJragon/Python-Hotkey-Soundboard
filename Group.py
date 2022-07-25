from random import random
from time import time

from GroupEntry import GroupEntry
from Hotkey import Hotkey
from SoundDirectory import SoundDirectory


class Group:
    def __init__(self,
                 sb,
                 name: str,
                 play_randomly: bool = True):
        self.soundboard = sb
        self.name = name
        self.playRandomly = play_randomly
        self.hotkeys: list[Hotkey] = []
        self.groupEntries: list[GroupEntry | SoundDirectory] = []
        self.weightSum = 0
        self.orderTracker = 0

    def play(self):
        delay = self.soundboard.options["Delay Before New Sound Can Play"].state
        if time() - self.soundboard.timeAtLastPlay <= delay or len(self.groupEntries) == 0:
            return
        self.soundboard.stopAllSounds = False
        self.soundboard.timeAtLastPlay = time()
        if self.playRandomly:
            self.weightSum = sum(e.weight for e in self.groupEntries)
            random_number = random() * self.weightSum
            for group_entry in self.groupEntries:
                if random_number <= group_entry.weight:
                    group_entry.play()
                    break
                else:
                    random_number -= group_entry.weight
        else:
            self.groupEntries[self.orderTracker].play()
            self.orderTracker += 1
            if self.orderTracker >= len(self.groupEntries):
                self.orderTracker = 0

    def swap_down(self, entry_index):
        if entry_index < len(self.groupEntries) - 1:
            temp = self.groupEntries[entry_index]
            self.groupEntries[entry_index] = self.groupEntries[entry_index + 1]
            self.groupEntries[entry_index + 1] = temp

    def swap_up(self, entry_index):
        if entry_index > 0:
            temp = self.groupEntries[entry_index]
            self.groupEntries[entry_index] = self.groupEntries[entry_index - 1]
            self.groupEntries[entry_index - 1] = temp

    def add_hotkey(self, name, keys):
        if self.soundboard.hotkey_exists(keys):
            return None
        hotkey = Hotkey(name, keys)
        self.hotkeys.append(hotkey)
        self.soundboard.hotkeyList.append(hotkey)
        return hotkey

    def hook_all_hotkeys(self):
        if not self.soundboard.options["Poll For Keyboard"].state:
            delay = self.soundboard.options["Delay Before New Sound Can Play"].state
            for hotkey in self.hotkeys:
                hotkey.hook(self.play, delay)

    def add_group_entry(self, path, weight):
        try:
            group_entry = GroupEntry(self.soundboard.find_or_create_entry_from_path(path), weight)
        except OSError:
            self.soundboard.set_device_to_default_and_refresh()
            group_entry = GroupEntry(self.soundboard.find_or_create_entry_from_path(path), weight)
        self.groupEntries.append(group_entry)
        return group_entry

    def add_directory(self, path, weight):
        dir_ = SoundDirectory(self.soundboard, path, weight)
        self.groupEntries.append(dir_)
        return dir_

    def remove_hotkey(self, hotkey):
        hotkey.unhook()
        self.hotkeys.remove(hotkey)
        self.soundboard.hotkeyList.remove(hotkey)
