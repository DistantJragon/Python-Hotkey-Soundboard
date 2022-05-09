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
defaultStreamsPerSoundEntry = options['defaultStreamsPerSoundEntry']['state']
stopAllSoundsWithNewSound = options['stopAllSoundsWithNewSound']['state']
pollForKeyboard = options['pollForKeyboard']['state']
pollingRate = options['pollingRate']['state']


def random_integer(min_range, max_range):
	x = math.floor(random.random() * (max_range - min_range + 1) + min_range)
	return x


portAudioInterface = pyaudio.PyAudio()
currentDeviceName = portAudioInterface.get_device_info_by_host_api_device_index(0, deviceIndex).get('name')
print("Device ID ", deviceIndex, " - ", currentDeviceName)


class Stream:
	def __init__(self, file_name, parent):
		self.parent = parent
		self.filePath = 'Sounds/' + file_name
		self.waveFile = wave.open(self.filePath, 'rb')
		self.stream = portAudioInterface.open(
			output_device_index=deviceIndex,
			format=portAudioInterface.get_format_from_width(self.waveFile.getsampwidth()),
			channels=self.waveFile.getnchannels(),
			rate=self.waveFile.getframerate(),
			output=True
		)
		self.timeAtLastPlay = time.time()
		self.isPlaying = False
		self.playSoundThread = threading.Thread(target=self.play_sound_entry)

	def play_sound_entry(self):
		self.waveFile = wave.open(self.filePath, 'rb')
		data = self.waveFile.readframes(chunk)
		while data:
			data = self.waveFile.readframes(chunk)
			self.stream.write(data)
			stop_sound = keyboard.is_pressed(stopAllSoundsHotkey)
			stop_sound = stop_sound or (stopAllSoundsWithNewSound and self.parent is not currentSoundPlaying)
			if stop_sound:
				break
		self.isPlaying = False
		self.parent.allStreamsArePlaying = False
		return


soundEntryList = {}


class Entry:
	def __init__(self, file_name, number_of_streams):
		global soundEntryList
		self.fileName = 'Sounds/' + file_name
		self.streamList = []
		self.allStreamsArePlaying = False
		self.timeAtLastPlay = time.time()
		while len(self.streamList) < number_of_streams:
			self.streamList.append(Stream(file_name, self))
		soundEntryList[file_name] = self

	def stream_with_earliest_play(self):
		earliest_stream = self.streamList[0]
		for stream in self.streamList:
			if stream.timeAtLastPlay < earliest_stream.timeAtLastPlay:
				earliest_stream = stream
		return earliest_stream


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
	allSoundsDictionary = {'playRandomly': True, 'hotkeys': [allSoundsGroupHotkey], 'numberOfStreams': 1, 'sounds': []}
	for sound in soundFilesNames:
		allSoundsDictionary['sounds'].append({'name': sound, 'weight': 1})
	groupList.append(allSoundsDictionary)
	for sound in soundFilesNames:
		Entry(sound + '.wav', 1)

groupFile = open('groupList.json')
groupData = json.load(groupFile)
groupEntries = groupData['groupEntries']
groupEntriesKeys = groupEntries.keys()
for key in groupEntriesKeys:
	groupList.append(groupEntries[key])
	if not makeGroupWithAllSounds:
		for sound in groupEntries[key]['sounds']:
			Entry(sound['name'] + '.wav', groupEntries[key]['numberOfStreams'])

for group in groupList:
	group['weightSum'] = 0
	for sound in group['sounds']:
		group['weightSum'] += sound['weight']
	group['orderTracker'] = 0

currentSoundPlaying = ''


def play_sound(sound_entry):
	global currentSoundPlaying
	if time.time() - sound_entry.timeAtLastPlay <= delayBeforeRestartSound:
		return
	currentSoundPlaying = sound_entry
	sound_entry.timeAtLastPlay = time.time()
	sound_entry.allStreamsArePlaying = True
	for stream in sound_entry.streamList:
		if not stream.isPlaying:
			stream.playSoundThread = threading.Thread(target=stream.play_sound_entry)
			stream.playSoundThread.start()
			stream.isPlaying = True
			stream.timeAtLastPlay = time.time()
			print("Playing " + sound_entry.fileName)
			sound_entry.allStreamsArePlaying = False
			break
	earliest_stream = sound_entry.stream_with_earliest_play()
	if sound_entry.allStreamsArePlaying:
		print("Playing " + sound_entry.fileName)
		earliest_stream.waveFile = wave.open(sound_entry.fileName, 'rb')
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
	while True:
		time.sleep(1)


keepRunningThread = threading.Thread(target=keep_program_running)
keepRunningThread.start()
print('Ready!')
