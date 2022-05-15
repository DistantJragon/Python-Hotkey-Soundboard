from json import load
from keyboard import is_pressed as is_hotkey_pressed, add_hotkey, unhook_all_hotkeys
from os import listdir
from pyaudio import PyAudio
from threading import Thread, Timer as Thread_Timer
from time import time
from typing import Callable, Optional
from wave import Wave_read
from Group import Group
from GroupEntry import GroupEntry
from Entry import Entry
from StreamList import StreamList
from Option import Option


def get_all_sound_file_names():
    list_of_files = listdir('Sounds')
    sound_files_names = [fileName for fileName in listdir('Sounds')]
    for file_name in list_of_files:
        if len(file_name) > 3 and file_name[-4:] == ".wav":
            sound_files_names.append(file_name)
            continue
    return sound_files_names


class Soundboard:
    def __init__(self):
        self.streamsList: list[StreamList] = []
        self.entryList: dict[str, Entry] = {}
        self.groupList: list[Group] = []
        self.options: dict[str, Option] = {}
        self.get_options()
        self.currentSoundPlaying: Optional[Wave_read] = None
        self.get_current_sound_playing: Callable[[], Optional[Wave_read]] = lambda: self.currentSoundPlaying
        self.userWantsToQuit: bool = False
        self.timeAtLastPlay: float = time()
        self.stopAllSounds = False
        self.get_stop_all_sounds = lambda: self.stopAllSounds

    def set_current_sound_playing(self, sound: Wave_read):
        self.currentSoundPlaying = sound

    def set_stop_all_sounds_true(self):
        self.stopAllSounds = True
        print("Stopping all sounds")

    def get_options(self):
        options_file = open('optionsList.json')
        options = load(options_file)
        for key in options:
            self.options[key] = Option(key, options[key])
        if self.options["Device"].state == -1:
            self.options["Device"].state = None

    def find_matching_stream(self, s_format: int, n_channels: int, rate: int):
        for unique_streams in self.streamsList:
            if (unique_streams.format == s_format and
                    unique_streams.channels == n_channels and
                    unique_streams.rate == rate):
                return unique_streams
        return None

    def make_group_and_entries_with_all_sounds(self):
        all_sounds_group_hotkey = self.options["\"All Sounds\" Group Hotkey"].state
        sound_files_names = get_all_sound_file_names()
        group_entries = []
        for sound_file in sound_files_names:
            if sound_file in self.entryList:
                current_entry = self.entryList[sound_file]
            else:
                current_entry = Entry(sound_file, self.find_or_create_stream_list_from_wav)
                self.entryList[sound_file] = current_entry
            group_entries.append(GroupEntry(current_entry, 1))
        self.groupList.append(Group(name="All Sounds Random",
                                    play_randomly=True,
                                    hotkeys=[all_sounds_group_hotkey],
                                    group_entries=group_entries))

    def add_group_file_to_group_list(self):
        group_file = open('groupList.json')
        group_entries = load(group_file)
        for key in group_entries:
            current_entries: list[GroupEntry] = []
            for jsonEntry in group_entries[key]["sounds"]:
                name = jsonEntry["name"] + ".wav"
                if name in self.entryList:
                    current_entry = self.entryList[name]
                else:
                    current_entry = Entry(name, self.find_or_create_stream_list_from_wav)
                    self.entryList[name] = current_entry
                current_entries.append(GroupEntry(current_entry, jsonEntry["weight"]))
            self.groupList.append(Group(name=key,
                                        play_randomly=group_entries[key]["playRandomly"],
                                        hotkeys=group_entries[key]["hotkeys"],
                                        group_entries=current_entries))

    def create_all_groups(self):
        if self.options["Make Group With All Sounds"].state:
            self.make_group_and_entries_with_all_sounds()
        self.add_group_file_to_group_list()

    def find_or_create_stream_list_from_wav(self, wav) -> StreamList:
        number_of_streams = self.options["Number Of Streams"].state
        temp_format = PyAudio().get_format_from_width(wav.getsampwidth())
        stream_list = self.find_matching_stream(temp_format,
                                                wav.getnchannels(),
                                                wav.getframerate())
        if stream_list is None:
            stream_list = StreamList(wav, number_of_streams, self.options["Device"].state)
            self.streamsList.append(stream_list)
        return stream_list

    def play_group(self, group: Group):
        self.stopAllSounds = False
        if time() - self.timeAtLastPlay <= self.options["Delay Before New Sound Can Play"].state:
            return
        self.timeAtLastPlay = time()
        group.play(self.options,
                   self.get_current_sound_playing,
                   self.set_current_sound_playing,
                   self.get_stop_all_sounds)

    def keep_program_running_poll(self):
        polling_rate = self.options['Polling Rate'].state
        if is_hotkey_pressed(self.options["\"Stop All Sounds\" Hotkey"].state):
            self.set_stop_all_sounds_true()
        for group in self.groupList:
            for hotkey in group.hotkeys:
                if is_hotkey_pressed(hotkey):
                    self.play_group(group)
                    break
        if self.userWantsToQuit:
            return
        t = Thread_Timer(polling_rate, self.keep_program_running_poll)
        t.start()

    def hook_hotkeys(self):
        delay_before_restart_sound = self.options['Delay Before New Sound Can Play'].state
        for group in self.groupList:
            for hotkey in group.hotkeys:
                add_hotkey(hotkey=hotkey,
                           callback=self.play_group,
                           args=(group,),
                           timeout=delay_before_restart_sound)
        add_hotkey(hotkey=self.options["\"Stop All Sounds\" Hotkey"].state,
                   callback=self.set_stop_all_sounds_true,
                   timeout=0.1)


def get_name_of_device(device_index):
    p = PyAudio()
    if device_index is None:
        return "Default"
    else:
        return p.get_device_info_by_host_api_device_index(0, device_index).get('name')


if __name__ == "__main__":
    s = Soundboard()
    s.create_all_groups()
    print("Using " + get_name_of_device(s.options["Device"].state) + " device")

    if s.options["Poll For Keyboard"].state:
        keepRunningThread = Thread(target=s.keep_program_running_poll)
        keepRunningThread.start()
    else:
        s.hook_hotkeys()
    print('Ready!')
    input()
    s.userWantsToQuit = True
    unhook_all_hotkeys()
