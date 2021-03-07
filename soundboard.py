import pyaudio
import wave
import sys
import keyboard
import threading

deviceIndex = 10

entryList = []

class Entry:
    def __init__(self, fileName, hotkeyList):
        self.fileName = 'Sounds/' + fileName + '.wav'
        self.hotkeyList = hotkeyList
        entryList.append(self)

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

eatPussyWithLips = Entry('Ricardo Pussy with lips', ['ctrl+l'])

playCurrentSoundEntry = True
while True:
    for soundEntry in entryList:
        playCurrentSoundEntry = True
        for hotkey in soundEntry.hotkeyList:
            if not keyboard.is_pressed(hotkey):
                playCurrentSoundEntry = False
            if not playCurrentSoundEntry:
                break
        if playCurrentSoundEntry:
            play_sound_entry(soundEntry.fileName)
