import pyaudio
import wave
import sys
import keyboard
import threading
import time

stopAllSoundsHotkey = 'ctrl+.'
delayBeforeRestartSound = 0.1
chunk = 2048
deviceIndex = 10

portAudioInterface = pyaudio.PyAudio()
soundEntryList = []
class Entry:
    def __init__(self, fileName, hotkey):
        self.fileName = 'Sounds/' + fileName + '.wav'
        self.hotkey = hotkey
        self.waveFile = wave.open(self.fileName, 'rb')
        self.stream = portAudioInterface.open(
            output_device_index = deviceIndex,
            format = portAudioInterface.get_format_from_width(self.waveFile.getsampwidth()),
            channels = self.waveFile.getnchannels(),
            rate = self.waveFile.getframerate(),
            output = True
        )
        self.playSoundThread = threading.Thread(target=self.play_sound_entry)
        self.isPlaying = False
        self.played = False
        self.timeAtLastPlay = time.time()
        soundEntryList.append(self)
    def play_sound_entry(self):
        self.waveFile = wave.open(self.fileName, 'rb')
        data = self.waveFile.readframes(chunk)
        while data:
            data = self.waveFile.readframes(chunk)
            self.stream.write(data)
            if keyboard.is_pressed(stopAllSoundsHotkey):
                break
            if keyboard.is_pressed(self.hotkey) and time.time() - self.timeAtLastPlay >= delayBeforeRestartSound:
                self.waveFile = wave.open(self.fileName, 'rb')
                self.timeAtLastPlay = time.time()
        self.isPlaying = False
        self.played = True

exampleSound = Entry('Ricardo boink', 'ctrl+num 1')
exampleSound2 = Entry('no i didnt', 'ctrl+num 2')

def detect_press_hotkey():
    while True:
        time.sleep(0.1)
        for entry in soundEntryList:
            if entry.played:
                entry.playSoundThread.join()
                entry.played = False
            if keyboard.is_pressed(entry.hotkey) and not entry.isPlaying and time.time() - entry.timeAtLastPlay >= delayBeforeRestartSound:
                entry.playSoundThread = threading.Thread(target=entry.play_sound_entry)
                entry.playSoundThread.start()
                entry.isPlaying = True
                entry.timeAtLastPlay = time.time()
                
mainThread = threading.Thread(target=detect_press_hotkey)
mainThread.start()