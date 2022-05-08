import pyaudio
import wave
import keyboard
import threading
import time
import os
import math
import random
import json

# Options
jsonFile = open('optionsList.json')
jsonData = json.load(jsonFile)
options = jsonData['options']
makeGroupWithAllSounds = options['makeGroupWithAllSounds']['state'] # Makes a sound entry using every sound in the Sounds folder that plays in a random order. Default: False
allSoundsGroupHotkey = options['allSoundsGroupHotkey']['state'] # Default: 'ctrl+num /'
stopAllSoundsHotkey = options['stopAllSoundsHotkey']['state'] # Default: 'ctrl+.'
delayBeforeRestartSound = options['delayBeforeRestartSound']['state'] # Prevents rapid-fire playing of sounds. Default: 0.1
chunk = options['chunk']['state'] # As I understand it, a buffer for pyAudio. This program defaults it to 2048. PyAudio defaulted it to 1024.
deviceIndex = options['deviceIndex']['state'] # Find the Device ID of your speakers or your Virtual Audio Cable with seeIndeciesOfDevices.py (Probably required). Default: 10
streamsPerSoundEntry = options['streamsPerSoundEntry']['state'] # How many times the same sound can overlap itself. Default: 3
stopAllSoundsWithNewSound = options['stopAllSoundsWithNewSound']['state'] # Stops all sounds if a new sound plays. Default: False

# Code
def randomInteger(min, max):
	x = math.floor(random.random() * (max - min + 1) + min)
	return x

portAudioInterface = pyaudio.PyAudio()
print("Device ID ", deviceIndex, " - ", portAudioInterface.get_device_info_by_host_api_device_index(0, deviceIndex).get('name'))
class Stream:
	def __init__(self, fileName, parent):
		self.parent = parent
		self.waveFile = wave.open(self.parent.fileName, 'rb')
		self.stream = portAudioInterface.open(
			output_device_index = deviceIndex,
			format = portAudioInterface.get_format_from_width(self.waveFile.getsampwidth()),
			channels = self.waveFile.getnchannels(),
			rate = self.waveFile.getframerate(),
			output = True
		)
		self.timeAtLastPlay = time.time()
		self.isPlaying = False
		self.playSoundThread = threading.Thread(target=self.play_sound_entry)
	def play_sound_entry(self):
		self.waveFile = wave.open(self.parent.fileName, 'rb')
		data = self.waveFile.readframes(chunk)
		while data:
			data = self.waveFile.readframes(chunk)
			self.stream.write(data)
			if keyboard.is_pressed(stopAllSoundsHotkey) or (stopAllSoundsWithNewSound and self.parent is not currentSoundPlaying):
				break
		self.isPlaying = False
		self.parent.allStreamsArePlaying = False
		return

soundEntryList = {}
class Entry:
	def __init__(self, fileName, numberOfStreams):
		global soundEntryList
		self.fileName = 'Sounds/' + fileName + '.wav'
		self.streamList = []
		self.allStreamsArePlaying = False
		self.timeAtLastPlay = time.time()
		while len(self.streamList) < numberOfStreams:
			self.streamList.append(Stream(fileName, self))
		soundEntryList[fileName] = self
	def streamWithEarliestPlay(self):
		earliestStream = self.streamList[0]
		for stream in self.streamList:
			if stream.timeAtLastPlay < earliestStream.timeAtLastPlay:
				earliestStream = stream
		return earliestStream

def getAllSoundFileNames():
	soundFilesNames = [fileName for fileName in os.listdir('Sounds')]
	for i in range(len(soundFilesNames)):
		if not '.wav' in soundFilesNames[i]:
			soundFilesNames.pop(i)
			continue
		soundFilesNames[i] = soundFilesNames[i][:-4]
	return soundFilesNames

groupList = []

if makeGroupWithAllSounds:
	soundFilesNames = getAllSoundFileNames()
	allSoundsDictionary = {'playRandomly':True, 'hotkeys':[allSoundsGroupHotkey], 'numberOfStreams':1}
	allSoundsDictionary['sounds'] = []
	for sound in soundFilesNames:
		allSoundsDictionary['sounds'].append({'name':sound, 'weight':1})
	groupList.append(allSoundsDictionary)
	for sound in soundFilesNames:
		Entry(sound, 1)

jsonFile = open('groupList.json')
jsonData = json.load(jsonFile)
groupEntries = jsonData['groupEntries']
groupEntriesKeys = groupEntries.keys()
for key in groupEntriesKeys:
	groupList.append(groupEntries[key])
	if not makeGroupWithAllSounds:
		for sound in groupEntries[key]['sounds']:
			Entry(sound['name'], groupEntries[key]['numberOfStreams'])

for group in groupList:
	group['weightSum'] = 0
	for sound in group['sounds']:
		group['weightSum'] += sound['weight']
	group['orderTracker'] = 0

currentSoundPlaying = ''

def playSound(soundEntry):
	global currentSoundPlaying
	if time.time() - soundEntry.timeAtLastPlay <= delayBeforeRestartSound:
		return
	currentSoundPlaying = soundEntry
	soundEntry.timeAtLastPlay = time.time()
	soundEntry.allStreamsArePlaying = True
	for stream in soundEntry.streamList:
		if not stream.isPlaying:
			stream.playSoundThread = threading.Thread(target=stream.play_sound_entry)
			stream.playSoundThread.start()
			stream.isPlaying = True
			stream.timeAtLastPlay = time.time()
			print("Playing " + soundEntry.fileName)
			soundEntry.allStreamsArePlaying = False
			break
	earliestStream = soundEntry.streamWithEarliestPlay()
	if soundEntry.allStreamsArePlaying:
		print("Playing " + soundEntry.fileName)
		earliestStream.waveFile = wave.open(soundEntry.fileName, 'rb')
		earliestStream.timeAtLastPlay = time.time()
	
def playSoundGroup(soundGroup):
	if soundGroup['playRandomly']:
		randomNumber = random.random() * soundGroup['weightSum']
		for sound in soundGroup['sounds']:
			if randomNumber <= sound['weight']:
				playSound(soundEntryList[sound['name']])
				break
			else:
				randomNumber -= sound['weight']
	else:
		soundInFrontOfLine = soundGroup['sounds'][soundGroup['orderTracker']]
		playSound(soundEntryList[soundInFrontOfLine['name']])
		soundGroup['orderTracker'] += 1
		if soundGroup['orderTracker'] > len(soundGroup['sounds']) - 1:
			soundGroup['orderTracker'] = 0

for group in groupList:
	for hotkey in group['hotkeys']:
		keyboard.add_hotkey(hotkey, playSoundGroup, args=(group,), timeout=delayBeforeRestartSound)

def keepProgramRunning():
	while True:
		time.sleep(1)
keepRunningThread = threading.Thread(target=keepProgramRunning)
keepRunningThread.start()

print('Ready!')