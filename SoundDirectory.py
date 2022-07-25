from os import listdir
from os.path import isdir
from random import choice


class SoundDirectory:
    def __init__(self,
                 sb,
                 dir_path,
                 weight):
        self.soundboard = sb
        self.filePath = dir_path
        self.exists = True if isdir(dir_path) else False
        self.name = dir_path.replace("/", "\\").split("\\")[-1]
        self.weight = weight if self.exists else 0
        self.entryList = []
        self.refresh_entry_list()

    def get_all_sound_file_paths(self):
        list_of_files = listdir(self.filePath)
        sound_files_names = []
        for file_name in list_of_files:
            if len(file_name) > 4 and file_name[-4:] == ".wav":
                sound_files_names.append(fr"{self.filePath}\{file_name}")
                continue
        return sound_files_names

    def refresh_entry_list(self):
        if not self.exists:
            return
        self.entryList.clear()
        for path in self.get_all_sound_file_paths():
            try:
                self.entryList.append(self.soundboard.find_or_create_entry_from_path(path))
            except OSError:
                self.soundboard.set_device_to_default_and_refresh()
                self.entryList.append(self.soundboard.find_or_create_entry_from_path(path))

    def play(self):
        if self.exists:
            choice(self.entryList).play()

    def refresh_stream_list(self):
        if not self.exists:
            return
        for entry in self.entryList:
            entry.refresh_stream_list()
