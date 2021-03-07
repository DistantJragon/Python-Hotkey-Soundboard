import pyaudio
import wave
import sys
import keyboard
import threading

deviceIndex = 10

entryList = []
class Entry:
    def __init__(self, fileName, hotkey):
        self.fileName = 'Sounds/' + fileName + '.wav'
        self.hotkey = hotkey
        entryList.append(self)

exampleSound = Entry('Ricardo boink', 'ctrl+l+d+f')

chunk = 1024
def play_sound_entry(fileName):
    waveFile = wave.open(fileName, 'rb')
    portAuidoInterface = pyaudio.PyAudio()
    stream = portAuidoInterface.open(
        output_device_index = deviceIndex,
        format = portAuidoInterface.get_format_from_width(waveFile.getsampwidth()),
        channels = waveFile.getnchannels(),
        rate = waveFile.getframerate(),
        output = True)
    data = waveFile.readframes(chunk)
    while len(data) > 0:
        stream.write(data)
        data = waveFile.readframes(chunk)
        if keyboard.is_pressed('ctrl+.'):
            break
    stream.stop_stream()
    stream.close()
    portAuidoInterface.terminate()

playCurrentSoundEntry = True
while True:
    for soundEntry in entryList:
        playCurrentSoundEntry = True
        if keyboard.is_pressed(soundEntry.hotkey):
            play_sound_entry(soundEntry.fileName)