import keyboard
import pyaudio
import threading
import time
from typing import Callable
from wave import open, Wave_read
from Option import Option


class Stream:
    def __init__(self,
                 device_index: int,
                 s_format: int, channels: int,
                 rate: int):
        self.format = s_format
        self.channels = channels
        self.rate = rate
        self.stream = pyaudio.PyAudio().open(
            output_device_index=device_index,
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
        )
        self.timeAtLastPlay = time.time()
        self.isPlaying = False
        self.playSoundThread = None
        self.wav = None

    def play(self,
             options: dict[str, Option],
             get_current_sound_playing: Callable[[], Wave_read]):
        stop_all_sounds_with_new_sound = options['Stop All Sounds With New Sound'].state
        stop_all_sounds_hotkey = options["\"Stop All Sounds\" Hotkey"].state
        chunk = options['Chunk Size'].state
        data = self.wav.readframes(chunk)
        self.isPlaying = True
        while data:
            data = self.wav.readframes(chunk)
            self.stream.write(data)
            if (keyboard.is_pressed(stop_all_sounds_hotkey) or
                    (stop_all_sounds_with_new_sound and
                     self.wav is not get_current_sound_playing())):
                break
        self.isPlaying = False
        return

    def get_play_thread(self,
                        options: dict[str, Option],
                        get_current_sound_playing: Callable[[], Wave_read]):
        return threading.Thread(target=self.play, args=(options, get_current_sound_playing))

    def set_wav(self, file_path):
        self.wav = open(file_path, 'rb')
