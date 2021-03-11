import pyaudio
import wave
import sys
import keyboard
import threading
import time
import os
import math
import random

# Options
stopAllSoundsHotkey = 'ctrl+.' # Default: 'ctrl+.'
delayBeforeRestartSound = 0.2 # Prevents rapid-fire playing of sounds. Default: 0.2
chunk = 2048 # As I understand it, a buffer for pyAudio. This program defaults in to 2048. PyAudio defaulted it to 1024.
deviceIndex = 10 # Find the Device ID of your speakers or your Virtual Audio Cable with seeIndeciesOfDevices.py (Probably required). Default: 10
streamsPerSoundEntry = 3 # How many times the same sound can overlap itself. Default: 3
stopAllSoundsWithNewSound = False # Stops all sounds if a new sound plays. Default: False

soundFiles = [f for f in os.listdir('Sounds')]
for i in range(len(soundFiles)):
	if not '.wav' in soundFiles[i]:
		soundFiles.pop(i)
		continue
	soundFiles[i] = soundFiles[i][:-4]

def randomInteger(min, max):
	x = math.floor(random.random() * (max - min + 1) + min)
	return x

portAudioInterface = pyaudio.PyAudio()
soundEntryList = []
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
		self.played = False
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
		self.played = True

class Entry:
	def __init__(self, fileName, hotkey):
		self.hotkey = hotkey
		self.fileName = 'Sounds/' + fileName + '.wav'
		self.streamList = []
		self.allStreamsArePlaying = False
		self.resetFirstStream = False
		self.timeAtLastPlay = time.time()
		for i in range(streamsPerSoundEntry):
			self.streamList.append(Stream(fileName, self))
		soundEntryList.append(self)
	def streamWithEarliestPlay(self, streamList):
		earliestStream = streamList[0]
		for stream in streamList:
			if stream.timeAtLastPlay < earliestStream.timeAtLastPlay:
				earliestStream = stream
		return earliestStream

# Add new sounds here
exampleSound = Entry('Ricardo boink', 'ctrl+num 1')
exampleSound2 = Entry('no i didnt', 'ctrl+num 2')
randomSound = Entry(soundFiles[randomInteger(0, len(soundFiles) - 1)], "ctrl+num /")

currentSoundPlaying = ''

def detect_press_hotkey():
	global currentSoundPlaying
	while True:
		time.sleep(0.05)
		for soundEntry in soundEntryList:
			for stream in soundEntry.streamList:
				if stream.played:
					stream.playSoundThread.join()
					stream.played = False
					soundEntry.allStreamsArePlaying = False
			if keyboard.is_pressed(soundEntry.hotkey) and time.time() - soundEntry.timeAtLastPlay >= delayBeforeRestartSound:
				currentSoundPlaying = soundEntry
				randomSound.fileName = 'Sounds/' + soundFiles[randomInteger(0, len(soundFiles) - 1)] + '.wav'
				for stream in soundEntry.streamList:
					if not stream.isPlaying:
						stream.playSoundThread = threading.Thread(target=stream.play_sound_entry)
						stream.playSoundThread.start()
						stream.isPlaying = True
						soundEntry.timeAtLastPlay = time.time()
						stream.timeAtLastPlay = time.time()
						break
					else:
						soundEntry.allStreamsArePlaying = True
				if soundEntry.allStreamsArePlaying and time.time() - soundEntry.timeAtLastPlay >= delayBeforeRestartSound:
					soundEntry.streamWithEarliestPlay(soundEntry.streamList).waveFile = wave.open(soundEntry.fileName, 'rb')
					soundEntry.streamWithEarliestPlay(soundEntry.streamList).timeAtLastPlay = time.time()
					soundEntry.timeAtLastPlay = time.time()

				
mainThread = threading.Thread(target=detect_press_hotkey)
mainThread.start()