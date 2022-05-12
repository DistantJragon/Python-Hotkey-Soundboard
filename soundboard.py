import pyaudio
import wave
import keyboard
import threading
import time
import os
import math
import random
import json

optionsFile = open('optionsList.json')
optionsData = json.load(optionsFile)
options = optionsData['options']

makeGroupWithAllSounds = options['makeGroupWithAllSounds']['state']
allSoundsGroupHotkey = options['allSoundsGroupHotkey']['state']
stopAllSoundsHotkey = options['stopAllSoundsHotkey']['state']
delayBeforeRestartSound = options['delayBeforeRestartSound']['state']
chunk = options['chunk']['state']
deviceIndex = options['deviceIndex']['state']
deviceName = options['deviceName']['state']
numberOfStreams = options['numberOfStreams']['state']
stopAllSoundsWithNewSound = options['stopAllSoundsWithNewSound']['state']
pollForKeyboard = options['pollForKeyboard']['state']
pollingRate = options['pollingRate']['state']

if deviceIndex == -1:
	deviceIndex = None


def random_integer(min_range, max_range):
	x = math.floor(random.random() * (max_range - min_range + 1) + min_range)
	return x


portAudioInterface = pyaudio.PyAudio()
if deviceIndex is None:
	print("Using default Windows playback device")
else:
	currentDeviceName = portAudioInterface.get_device_info_by_host_api_device_index(0, deviceIndex).get('name')
	print("Using playback device ID ", deviceIndex, " - ", currentDeviceName)

streamsList = []
currentSoundPlaying = None


def stream_with_earliest_play(stream_list):
	earliest_stream = stream_list[0]
	for stream in stream_list:
		if stream.timeAtLastPlay < earliest_stream.timeAtLastPlay:
			earliest_stream = stream
	return earliest_stream


class Stream:
	def __init__(self, template_wav):
		self.format = portAudioInterface.get_format_from_width(template_wav.getsampwidth())
		self.channels = template_wav.getnchannels()
		self.rate = template_wav.getframerate()
		self.stream = portAudioInterface.open(
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
		global currentSoundPlaying
		data = self.wav.readframes(chunk)
		while data:
			data = self.wav.readframes(chunk)
			self.stream.write(data)
			stop_sound = keyboard.is_pressed(stopAllSoundsHotkey)
			stop_sound = stop_sound or (stopAllSoundsWithNewSound and self.wav is not currentSoundPlaying)
			if stop_sound:
				break
		self.isPlaying = False
		return

	def get_thread_play_sound(self):
		return threading.Thread(target=self.play_sound_entry)

	def set_wav(self, file_path):
		self.wav = wave.open(file_path, 'rb')


soundEntryList = {}


def find_matching_stream(stream_format, n_channels, rate):
	global streamsList
	for streams in streamsList:
		if streams[0].format != stream_format:
			continue
		if streams[0].channels != n_channels:
			continue
		if streams[0].rate != rate:
			continue
		return streams
	return None


class Entry:
	def __init__(self, file_name, number_of_streams):
		global soundEntryList
		global streamsList
		self.filePath = 'Sounds/' + file_name
		self.timeAtLastPlay = time.time()
		self.wav = wave.open(self.filePath, 'rb')
		soundEntryList[file_name] = self
		temp_format = portAudioInterface.get_format_from_width(self.wav.getsampwidth())
		self.streamList = find_matching_stream(temp_format, self.wav.getnchannels(), self.wav.getframerate())
		if self.streamList is None:
			new_streams = []
			for i in range(number_of_streams):
				new_streams.append(Stream(self.wav))
			self.streamList = new_streams
			streamsList.append(new_streams)


def get_all_sound_file_names():
	sound_files_names = [fileName for fileName in os.listdir('Sounds')]
	for i in range(len(sound_files_names)):
		if '.wav' not in sound_files_names[i]:
			sound_files_names.pop(i)
			continue
		sound_files_names[i] = sound_files_names[i][:-4]
	return sound_files_names


groupList = []

if makeGroupWithAllSounds:
	soundFilesNames = get_all_sound_file_names()
	allSoundsDictionary = {'playRandomly': True, 'hotkeys': [allSoundsGroupHotkey], 'sounds': []}
	for sound in soundFilesNames:
		allSoundsDictionary['sounds'].append({'name': sound, 'weight': 1})
	groupList.append(allSoundsDictionary)
	for sound in soundFilesNames:
		Entry(sound + '.wav', numberOfStreams)

groupFile = open('groupList.json')
groupData = json.load(groupFile)
groupEntries = groupData['groupEntries']
groupEntriesKeys = groupEntries.keys()
for key in groupEntriesKeys:
	groupList.append(groupEntries[key])
	if not makeGroupWithAllSounds:
		for sound in groupEntries[key]['sounds']:
			Entry(sound['name'] + '.wav', numberOfStreams)

for group in groupList:
	group['weightSum'] = 0
	for sound in group['sounds']:
		group['weightSum'] += sound['weight']
	group['orderTracker'] = 0


def play_sound(sound_entry):
	global currentSoundPlaying
	if time.time() - sound_entry.timeAtLastPlay <= delayBeforeRestartSound:
		return
	sound_entry.timeAtLastPlay = time.time()
	sound_entry.allStreamsArePlaying = True
	for stream in sound_entry.streamList:
		if not stream.isPlaying:
			stream.set_wav(sound_entry.filePath)
			currentSoundPlaying = stream.wav
			stream.playSoundThread = stream.get_thread_play_sound()
			stream.playSoundThread.start()
			stream.isPlaying = True
			stream.timeAtLastPlay = time.time()
			print("Playing " + sound_entry.filePath)
			sound_entry.allStreamsArePlaying = False
			break
	earliest_stream = stream_with_earliest_play(sound_entry.streamList)
	if sound_entry.allStreamsArePlaying:
		print("Playing " + sound_entry.filePath)
		earliest_stream.set_wav(sound_entry.filePath)
		currentSoundPlaying = earliest_stream.wav
		earliest_stream.timeAtLastPlay = time.time()


def play_sound_group(sound_group):
	if sound_group['playRandomly']:
		random_number = random.random() * sound_group['weightSum']
		for current_sound in sound_group['sounds']:
			if random_number <= current_sound['weight']:
				play_sound(soundEntryList[current_sound['name'] + ".wav"])
				break
			else:
				random_number -= current_sound['weight']
	else:
		sound_in_front_of_line = sound_group['sounds'][sound_group['orderTracker']]
		play_sound(soundEntryList[sound_in_front_of_line['name'] + ".wav"])
		sound_group['orderTracker'] += 1
		if sound_group['orderTracker'] > len(sound_group['sounds']) - 1:
			sound_group['orderTracker'] = 0


for group in groupList:
	for hotkey in group['hotkeys']:
		keyboard.add_hotkey(hotkey, play_sound_group, args=(group,), timeout=delayBeforeRestartSound)


def keep_program_running():
	input()


keepRunningThread = threading.Thread(target=keep_program_running)
keepRunningThread.start()
print('Ready!')
