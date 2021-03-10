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
streamsPerSoundEntry = 3

portAudioInterface = pyaudio.PyAudio()
soundEntryList = []

class Stream:
    def __init__(self, fileName):
        self.fileName = 'Sounds/' + fileName + '.wav'
        self.waveFile = wave.open(self.fileName, 'rb')
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
        self.waveFile = wave.open(self.fileName, 'rb')
        data = self.waveFile.readframes(chunk)
        while data:
            data = self.waveFile.readframes(chunk)
            self.stream.write(data)
            if keyboard.is_pressed(stopAllSoundsHotkey):
                break
        self.isPlaying = False
        self.played = True

class Entry:
    def __init__(self, fileName, hotkey):
        self.hotkey = hotkey
        self.streamList = []
        self.allStreamsArePlaying = False
        self.resetFirstStream = False
        self.timeAtLastPlay = time.time()
        for i in range(streamsPerSoundEntry):
            self.streamList.append(Stream(fileName))
        soundEntryList.append(self)
    def streamWithEarliestPlay(self, streamList):
        earliestStream = streamList[0]
        for stream in streamList:
            if stream.timeAtLastPlay < earliestStream.timeAtLastPlay:
                earliestStream = stream
        return earliestStream

exampleSound = Entry('Ricardo boink', 'ctrl+num 1')
exampleSound2 = Entry('weiland Fuck. my. dick. off. gam. ers. eeeerrrww', 'ctrl+num 2')

def detect_press_hotkey():
    while True:
        time.sleep(0.05)
        for soundEntry in soundEntryList:
            for stream in soundEntry.streamList:
                if stream.played:
                    stream.playSoundThread.join()
                    stream.played = False
                    soundEntry.allStreamsArePlaying = False
            if keyboard.is_pressed(soundEntry.hotkey) and time.time() - soundEntry.timeAtLastPlay >= delayBeforeRestartSound:
                for stream in soundEntry.streamList:
                    if not stream.isPlaying:  
                        stream.playSoundThread = threading.Thread(target=stream.play_sound_entry)
                        stream.playSoundThread.start()
                        stream.isPlaying = True
                        soundEntry.timeAtLastPlay = time.time()
                        stream.timeAtLastPlay = time.time()
                        print(1)
                        break
                    else:
                        soundEntry.allStreamsArePlaying = True
                if soundEntry.allStreamsArePlaying and time.time() - soundEntry.timeAtLastPlay >= delayBeforeRestartSound:
                    print(2)
                    soundEntry.streamWithEarliestPlay(soundEntry.streamList).waveFile = wave.open(stream.fileName, 'rb')
                    soundEntry.streamWithEarliestPlay(soundEntry.streamList).timeAtLastPlay = time.time()
                    soundEntry.timeAtLastPlay = time.time()

                
mainThread = threading.Thread(target=detect_press_hotkey)
mainThread.start()