from threading import Thread
from time import time
from wave import open


class Stream:
    def __init__(self, sb, device_index, s_format, channels, rate):
        self.soundboard = sb
        self.format = s_format
        self.channels = channels
        self.rate = rate
        self.stream = sb.pyAudio.open(
            output_device_index=device_index,
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
        )
        self.timeAtLastPlay = time()
        self.isPlaying = False
        self.playSoundThread = None
        self.wav = None

    def play(self):
        options = self.soundboard.options
        def stop(): return self.soundboard.stopAllSounds
        current_sound = self.soundboard.currentSoundPlaying
        new_sound_stop = options['Stop All Sounds With New Sound'].state
        chunk = options['Chunk Size'].state
        data = self.wav.readframes(chunk)
        self.isPlaying = True
        while data and not stop() and not (new_sound_stop and self.wav is not current_sound):
            data = self.wav.readframes(chunk)
            self.stream.write(data)
        self.isPlaying = False

    def get_play_thread(self):
        return Thread(target=self.play, args=())

    def set_wav(self, file_path):
        self.wav = open(file_path, 'rb')

    def matches_info(self, s_format, channels, rate):
        return (self.format == s_format and
                self.channels == channels and
                self.rate == rate)
