from json import load, dumps
from keyboard import is_pressed as is_hotkey_pressed
from os.path import isdir
from pyaudio import PyAudio
from threading import Thread
from time import time

from Entry import Entry
from Group import Group
from Hotkey import Hotkey
from Option import Option
from Stream import Stream


def path_has_extension(path):
    if path.replace("/", "\\").split("\\")[-1].count(".") > 0:
        return True
    else:
        return False


class Soundboard:
    def __init__(self):
        self.streamsList = []
        self.hotkeyList = []
        self.entryList = {}
        self.groupList = []
        self.options = {}
        self.pyAudio = PyAudio()
        self.devices = {}
        number_of_devices = self.pyAudio.get_host_api_info_by_index(0).get('deviceCount')
        for i in range(number_of_devices):
            self.devices[i] = self.pyAudio.get_device_info_by_host_api_device_index(0, i).get('name')
        self.currentSoundPlaying = None
        self.stopThread = False
        self.timeAtLastPlay = time()
        self.stopAllSounds = False
        self.stopAllSoundsHotkey = None
        self.runThread = None

    def set_stop_all_sounds_true(self):
        self.stopAllSounds = True

    def update_options(self):
        with open("options.json") as options_file:
            options_and_info = load(options_file)
            if len(self.options) == 0:
                for key, value in options_and_info.items():
                    self.options[key] = Option(key, value)
            else:
                for key, value in options_and_info.items():
                    self.options[key].state = value["state"]

            device_index = self.options["Device"].state
            try:
                device_index_name = self.pyAudio.get_device_info_by_host_api_device_index(0, device_index).get('name')
            except TypeError:
                device_index_name = "Default"
            except OSError:
                device_index_name = "Not found"
            device_name = self.options["Device Name"].state
            if device_name == "Default":
                self.options["Device"].state = None
            elif device_index_name != device_name:
                self.options["Device"].state = [i for i, d in self.devices.items() if d == device_name][0]

        hk_name = list(self.options["\"Stop All Sounds\" Hotkey"].state.keys())[0]
        hk_keys = list(self.options["\"Stop All Sounds\" Hotkey"].state.values())[0]
        if self.stopAllSoundsHotkey is None:
            self.stopAllSoundsHotkey = Hotkey(hk_name, hk_keys)
            self.hotkeyList.append(self.stopAllSoundsHotkey)
        else:
            self.stopAllSoundsHotkey.name, self.stopAllSoundsHotkey.keys = hk_name, hk_keys

    def find_matching_stream(self, s_format, n_channels, rate):
        for unique_streams in self.streamsList:
            if unique_streams[0].matches_info(s_format, n_channels, rate):
                return unique_streams
        return None

    def add_group_file_to_group_list(self):
        with open('groupList.json') as group_file:
            group_entries = load(group_file)
            for group_name, json_group in group_entries.items():
                self.groupList.append(Group(self, group_name, json_group["playRandomly"]))
                for json_hotkey_name, json_hotkey_keys in json_group["hotkeys"].items():
                    self.groupList[-1].add_hotkey(json_hotkey_name, json_hotkey_keys)
                for json_entry in json_group["sounds"]:
                    if len(json_entry["path"]) >= 4 and json_entry["path"][-4:] == ".wav":
                        self.groupList[-1].add_group_entry(json_entry["path"], json_entry["weight"])
                    elif isdir(json_entry["path"]) or not path_has_extension(json_entry["path"]):
                        self.groupList[-1].add_directory(json_entry["path"], json_entry["weight"])
                    # else:
                    #     raise FileNotFoundError("File is not a folder or a WAV file")

    def find_or_create_stream_list_from_wav(self, wav):
        number_of_streams = self.options["Number Of Streams"].state
        temp_format = self.pyAudio.get_format_from_width(wav.getsampwidth())
        stream_list = self.find_matching_stream(temp_format,
                                                wav.getnchannels(),
                                                wav.getframerate())
        if stream_list is None:
            device_index = self.options["Device"].state
            stream_list = []
            for i in range(number_of_streams):
                stream_list.append(Stream(self, device_index, temp_format, wav.getnchannels(), wav.getframerate()))
            self.streamsList.append(stream_list)
        return stream_list

    def find_or_create_entry_from_path(self, path) -> Entry:
        if path not in self.entryList:
            self.entryList[path] = Entry(self, path)
        return self.entryList[path]

    def poll_keyboard(self):
        polling_rate = self.options['Polling Rate'].state
        if is_hotkey_pressed(tuple(self.stopAllSoundsHotkey.keys)):
            self.set_stop_all_sounds_true()
        for group in self.groupList:
            for hotkey in group.hotkeys:
                if is_hotkey_pressed(tuple(hotkey.keys)):
                    group.play()
                    break
        if self.stopThread:
            return
        from threading import Timer as Thread_Timer
        t = Thread_Timer(polling_rate, self.poll_keyboard)
        t.start()

    def hook_all_hotkeys(self):
        if not self.options["Poll For Keyboard"].state:
            for group in self.groupList:
                group.hook_all_hotkeys()
            self.stopAllSoundsHotkey.hook(self.set_stop_all_sounds_true, 0.1)

    def delete_group(self, group):
        for hotkey in group.hotkeys:
            hotkey.unhook()
            del hotkey
        self.groupList.remove(group)
        del group

    def hotkey_exists(self, keys):
        for hotkey in self.hotkeyList:
            all_keys_in_hotkey = True
            for key in keys:
                if key not in hotkey.keys:
                    all_keys_in_hotkey = False
                    break
            if all_keys_in_hotkey:
                return True
        return False

    def save_options(self):
        options_dict = {}
        stop_all_sounds = self.options["\"Stop All Sounds\" Hotkey"]
        stop_all_sounds.state.clear()
        stop_all_sounds.state[self.stopAllSoundsHotkey.name] = self.stopAllSoundsHotkey.keys
        for name, option in self.options.items():
            inner_dict = {"description": option.description, "state": option.state}
            options_dict[name] = inner_dict
        with open("options.json", "w") as options_file:
            options_file.write(dumps(options_dict, indent=4))

    def save_groups(self):
        groups_dict = {}
        for group in self.groupList:
            hotkey_dict = {}
            for hotkey in group.hotkeys:
                hotkey_dict[hotkey.name] = hotkey.keys
            sounds_list = []
            for entry in group.groupEntries:
                sounds_list.append({"path": entry.filePath, "weight": int(entry.weight)})
            group_dict = {"playRandomly": group.playRandomly,
                          "hotkeys": hotkey_dict,
                          "sounds": sounds_list}
            groups_dict[group.name] = group_dict
        with open("groupList.json", "w") as group_file:
            group_file.write(dumps(groups_dict, indent=4))

    def update_stop_all_sounds_hotkey(self, name, keys):
        self.stopAllSoundsHotkey.unhook()
        self.stopAllSoundsHotkey.name, self.stopAllSoundsHotkey.keys = name, keys
        if not self.options["Poll For Keyboard"].state:
            self.stopAllSoundsHotkey.hook(self.set_stop_all_sounds_true, 0.1)

    def refresh_all_streams(self):
        self.streamsList.clear()
        for group in self.groupList:
            for group_entry in group.groupEntries:
                group_entry.refresh_stream_list()

    def set_device_to_default_and_refresh(self):
        self.options["Device"].state = None
        self.options["Device Name"].state = "Default"
        self.refresh_all_streams()

    def start(self):
        self.update_options()
        self.refresh_all_streams()
        if self.options["Poll For Keyboard"].state:
            self.runThread = Thread(target=self.poll_keyboard)
            self.runThread.start()
        else:
            self.hook_all_hotkeys()

    def restart(self):
        if self.runThread is not None:
            self.stopThread = True
            self.runThread.join()
            self.runThread = None
            self.stopThread = False
        for hotkey in self.hotkeyList:
            hotkey.unhook()
        self.start()
