from json import load
from keyboard import is_pressed as is_hotkey_pressed, add_hotkey, unhook_all_hotkeys
from os import listdir
from pyaudio import PyAudio
from threading import Thread, Timer as Thread_Timer
from time import time
from typing import Callable, Optional
from wave import Wave_read
from Group import Group
from Entry import Entry
from StreamList import StreamList
from Option import Option


def get_all_sound_file_names():
    sound_files_names = [fileName for fileName in listdir('Sounds')]
    for i in range(len(sound_files_names)):
        if '.wav' not in sound_files_names[i]:
            sound_files_names.pop(i)
            continue
        sound_files_names[i] = sound_files_names[i][:-4]
    return sound_files_names


class Soundboard:
    def __init__(self):
        self.streamsList: list[StreamList] = []
        self.entryList: dict[str, Entry] = {}
        self.groupList: list[Group] = []
        self.allEntriesMade: bool = False
        self.options: dict[str, Option] = {}
        self.get_options()
        self.currentSoundPlaying: Optional[Wave_read] = None
        self.get_current_sound_playing: Callable[[], Optional[Wave_read]] = lambda: self.currentSoundPlaying
        self.userWantsToQuit: bool = False
        self.timeAtLastPlay: float = time()

    def set_current_sound_playing(self, sound: Wave_read):
        self.currentSoundPlaying = sound

    def get_options(self):
        options_file = open('optionsList.json')
        options_data = load(options_file)
        options = options_data['options']
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
        entry_dictionary = {}
        for sound_file in sound_files_names:
            current_entry = Entry(sound_file + '.wav', self.find_or_create_stream_list_from_wav)
            self.entryList[sound_file] = current_entry
            entry_dictionary[current_entry] = 1
        self.groupList.append(Group(name="All Sounds Random",
                                    play_randomly=True,
                                    hotkeys=[all_sounds_group_hotkey],
                                    sound_entries_weights=entry_dictionary))
        self.allEntriesMade = False

    def add_group_file_to_group_list(self):
        group_file = open('groupList.json')
        group_data = load(group_file)
        group_entries = group_data['groupEntries']
        for key in group_entries:
            current_entries = {}
            for jsonEntry in group_entries[key]["sounds"]:
                if jsonEntry["name"] + ".wav" in self.entryList:
                    current_entry = self.entryList[jsonEntry["name"] + ".wav"]
                else:
                    current_entry = Entry(jsonEntry["name"] + ".wav", self.find_or_create_stream_list_from_wav)
                    self.entryList[jsonEntry["name"]] = current_entry
                current_entries[current_entry] = jsonEntry["weight"]
            self.groupList.append(Group(name=key,
                                        play_randomly=group_entries[key]["playRandomly"],
                                        hotkeys=group_entries[key]["hotkeys"],
                                        sound_entries_weights=current_entries))

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

    @staticmethod
    def keep_program_running_events():
        input()
        unhook_all_hotkeys()

    def play_group(self,
                   group: Group):
        if time() - self.timeAtLastPlay <= self.options["Delay Before New Sound Can Play"].state:
            return
        self.timeAtLastPlay = time()
        group.play(self.options,
                   self.get_current_sound_playing,
                   self.set_current_sound_playing)

    def keep_program_running_poll(self):
        polling_rate = self.options['Polling Rate'].state
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
                add_hotkey(hotkey,
                           self.play_group,
                           args=(group,),
                           timeout=delay_before_restart_sound)


def get_name_of_device(device_index):
    p = PyAudio()
    if device_index is None:
        return "Default"
    else:
        return p.get_device_info_by_host_api_device_index(0, device_index).get('name')


if __name__ == "__main__":
    s = Soundboard()
    if s.options["Make Group With All Sounds"].state:
        s.make_group_and_entries_with_all_sounds()
    s.add_group_file_to_group_list()
    # deviceName = options['deviceName']['state']
    print("Using " + get_name_of_device(s.options["Device"].state) + " device")

    if s.options["Poll For Keyboard"].state:
        keepRunningThread = Thread(target=s.keep_program_running_poll)
        keepRunningThread.start()
        print('Ready!')
        input()
        s.userWantsToQuit = True
    else:
        s.hook_hotkeys()
        keepRunningThread = Thread(target=s.keep_program_running_events)
        keepRunningThread.start()
        print('Ready!')
