import pyaudio
import wave
import sys
import keyboard
import threading
import time

stopAllSoundsHotkey = 'ctrl+.'
portAudioInterface = pyaudio.PyAudio()
chunk = 2048
deviceIndex = 10

entryList = []
class Entry:
    def __init__(self, fileName, hotkey):
        self.fileName = 'Sounds/' + fileName + '.wav'
        self.hotkey = hotkey
        self.playSoundThread = threading.Thread(target=self.play_sound_entry)
        self.playSoundThread.start()
    def play_sound_entry(self):
        while True:
            self.waveFile = wave.open(self.fileName, 'rb')
            self.stream = portAudioInterface.open(
                output_device_index = deviceIndex,
                format = portAudioInterface.get_format_from_width(self.waveFile.getsampwidth()),
                channels = self.waveFile.getnchannels(),
                rate = self.waveFile.getframerate(),
                output = True
            )
            while True:
                if keyboard.is_pressed(self.hotkey):
                    break
                time.sleep(0.1)
            data = self.waveFile.readframes(chunk)
            while data:
                data = self.waveFile.readframes(chunk)
                self.stream.write(data)
                if keyboard.is_pressed(stopAllSoundsHotkey):
                    break
            self.stream.stop_stream()
            self.stream.close()

exampleSound = Entry('Ricardo boink', 'ctrl+1')
exampleSound2 = Entry('no i didnt', 'ctrl+2')
