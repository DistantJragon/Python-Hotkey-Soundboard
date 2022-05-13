import pyaudio
import wave
import keyboard
import threading
import time
import os
import math
import random
import json


def random_integer(min_range, max_range):
    x = math.floor(random.random() * (max_range - min_range + 1) + min_range)
    return x


def get_all_sound_file_names():
    sound_files_names = [fileName for fileName in os.listdir('Sounds')]
    for i in range(len(sound_files_names)):
        if '.wav' not in sound_files_names[i]:
            sound_files_names.pop(i)
            continue
        sound_files_names[i] = sound_files_names[i][:-4]
    return sound_files_names


def print_playback_device(device_index):
    p = pyaudio.PyAudio()
    if device_index is None:
        print("Using default Windows playback device")
    else:
        current_device_name = p.get_device_info_by_host_api_device_index(0, device_index).get('name')
        print("Using playback device ID ", device_index, " - ", current_device_name)


optionsFile = open('optionsList.json')
optionsData = json.load(optionsFile)
options = optionsData['options']
currentSoundPlaying = None
deviceIndex = options['deviceIndex']['state']
if deviceIndex == -1:
    deviceIndex = None


class Stream:
    def __init__(self, template_wav):
        global deviceIndex
        self.format = pyaudio.PyAudio().get_format_from_width(template_wav.getsampwidth())
        self.channels = template_wav.getnchannels()
        self.rate = template_wav.getframerate()
        self.stream = pyaudio.PyAudio().open(
            output_device_index=deviceIndex,
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
        )
        self.timeAtLastPlay = time.time()
        self.isPlaying = False
        self.playSoundThread = None
        self.wav = None

    def play_sound_entry(self):
        global currentSoundPlaying, options
        stop_all_sounds_with_new_sound = options['stopAllSoundsWithNewSound']['state']
        stop_all_sounds_hotkey = options['stopAllSoundsHotkey']['state']
        chunk = options['chunk']['state']
        data = self.wav.readframes(chunk)
        self.isPlaying = True
        while data:
            data = self.wav.readframes(chunk)
            self.stream.write(data)
            stop_sound = keyboard.is_pressed(stop_all_sounds_hotkey)
            stop_sound = stop_sound or (stop_all_sounds_with_new_sound and self.wav is not currentSoundPlaying)
            if stop_sound:
                break
        self.isPlaying = False
        return

    def get_thread_play_sound(self):
        return threading.Thread(target=self.play_sound_entry)

    def set_wav(self, file_path):
        self.wav = wave.open(file_path, 'rb')


def stream_with_earliest_play(stream_list):
    earliest_stream = stream_list[0]
    for stream in stream_list:
        if stream.timeAtLastPlay < earliest_stream.timeAtLastPlay:
            earliest_stream = stream
    return earliest_stream


def find_matching_stream(streams_list, stream_format, n_channels, rate):
    for streams in streams_list:
        if streams[0].format != stream_format:
            continue
        if streams[0].channels != n_channels:
            continue
        if streams[0].rate != rate:
            continue
        return streams
    return None


streamsList = []
soundEntryList = {}
delayBeforeRestartSound = options['delayBeforeRestartSound']['state']


class Entry:
    def __init__(self, file_name, number_of_streams):
        global soundEntryList, streamsList
        self.filePath = 'Sounds/' + file_name
        self.timeAtLastPlay = time.time()
        self.wav = wave.open(self.filePath, 'rb')
        soundEntryList[file_name] = self
        temp_format = pyaudio.PyAudio().get_format_from_width(self.wav.getsampwidth())
        self.streamList = find_matching_stream(streamsList,
                                               temp_format,
                                               self.wav.getnchannels(),
                                               self.wav.getframerate())
        self.allStreamsArePlaying = False
        if self.streamList is None:
            new_streams = []
            for i in range(number_of_streams):
                new_streams.append(Stream(self.wav))
            self.streamList = new_streams
            streamsList.append(new_streams)

    def play(self):
        global currentSoundPlaying, delayBeforeRestartSound
        if time.time() - self.timeAtLastPlay <= delayBeforeRestartSound:
            return
        self.timeAtLastPlay = time.time()
        self.allStreamsArePlaying = True
        for stream in self.streamList:
            if not stream.isPlaying:
                stream.set_wav(self.filePath)
                currentSoundPlaying = stream.wav
                stream.playSoundThread = stream.get_thread_play_sound()
                stream.playSoundThread.start()
                stream.isPlaying = True
                stream.timeAtLastPlay = time.time()
                print("Playing " + self.filePath)
                self.allStreamsArePlaying = False
                break
        if self.allStreamsArePlaying:
            print("Playing " + self.filePath)
            earliest_stream = stream_with_earliest_play(self.streamList)
            earliest_stream.set_wav(self.filePath)
            currentSoundPlaying = earliest_stream.wav
            earliest_stream.timeAtLastPlay = time.time()


groupList = []
numberOfStreams = options['numberOfStreams']['state']


def make_group_and_entries_with_all_sounds():
    global groupList, options, numberOfStreams
    all_sounds_group_hotkey = options['allSoundsGroupHotkey']['state']
    sound_files_names = get_all_sound_file_names()
    all_sounds_dictionary = {'playRandomly': True, 'hotkeys': [all_sounds_group_hotkey], 'sounds': []}
    for sound_file in sound_files_names:
        all_sounds_dictionary['sounds'].append({'name': sound_file, 'weight': 1})
    groupList.append(all_sounds_dictionary)
    for sound_file in sound_files_names:
        Entry(sound_file + '.wav', numberOfStreams)


def add_group_file_to_group_list():
    group_file = open('groupList.json')
    group_data = json.load(group_file)
    group_entries = group_data['groupEntries']
    group_entries_keys = group_entries.keys()
    make_group_with_all_sounds = options['makeGroupWithAllSounds']['state']

    for key in group_entries_keys:
        groupList.append(group_entries[key])
        if not make_group_with_all_sounds:
            for sound_file_name in group_entries[key]['sounds']:
                Entry(sound_file_name['name'] + '.wav', numberOfStreams)


def play_sound_group(sound_group):
    if sound_group['playRandomly']:
        random_number = random.random() * sound_group['weightSum']
        for current_sound in sound_group['sounds']:
            if random_number <= current_sound['weight']:
                soundEntryList[current_sound['name'] + ".wav"].play()
                break
            else:
                random_number -= current_sound['weight']
    else:
        sound_in_front_of_line = sound_group['sounds'][sound_group['orderTracker']]
        soundEntryList[sound_in_front_of_line['name'] + ".wav"].play()
        sound_group['orderTracker'] += 1
        if sound_group['orderTracker'] > len(sound_group['sounds']) - 1:
            sound_group['orderTracker'] = 0


def keep_program_running_events():
    input()
    keyboard.unhook_all_hotkeys()


def check_keys():
    global delayBeforeRestartSound
    for t_group in groupList:
        for t_hotkey in t_group['hotkeys']:
            if keyboard.is_pressed(t_hotkey):
                play_sound_group(t_group)
                time.sleep(delayBeforeRestartSound)
                break


userQuit = False
pollingRate = options['pollingRate']['state']


def keep_program_running_poll():
    global userQuit, pollingRate
    while not userQuit:
        check_keys()
        time.sleep(pollingRate)


def add_fields_to_groups():
    for group in groupList:
        group['weightSum'] = 0
        for sound in group['sounds']:
            group['weightSum'] += sound['weight']
        group['orderTracker'] = 0


def hook_hotkeys():
    global groupList, delayBeforeRestartSound
    for group in groupList:
        for hotkey in group['hotkeys']:
            keyboard.add_hotkey(hotkey, play_sound_group, args=(group,), timeout=delayBeforeRestartSound)


if __name__ == "__main__":
    makeGroupWithAllSounds = options['makeGroupWithAllSounds']['state']
    # deviceName = options['deviceName']['state']
    pollForKeyboard = options['pollForKeyboard']['state']
    print_playback_device(deviceIndex)

    if makeGroupWithAllSounds:
        make_group_and_entries_with_all_sounds()
    add_group_file_to_group_list()
    add_fields_to_groups()

    if pollForKeyboard:
        keepRunningThread = threading.Thread(target=keep_program_running_poll)
        keepRunningThread.start()
        print('Ready! Since polling is on, the program will not print what sound was played')
        input()
        userQuit = True
    else:
        hook_hotkeys()
        keepRunningThread = threading.Thread(target=keep_program_running_events)
        keepRunningThread.start()
        print('Ready!')
