from time import time
from typing import Callable
from wave import open, Wave_read
from Option import Option
from StreamList import StreamList


class Entry:
    def __init__(self,
                 file_name: str,
                 get_stream_list: Callable[[Wave_read], StreamList]):
        self.filePath = 'Sounds/' + file_name
        self.timeAtLastPlay = time()
        self.wav = open(self.filePath, 'rb')
        self.streamList = get_stream_list(self.wav)

    def play(self,
             options: dict[str, Option],
             get_current_sound_playing: Callable[[], Wave_read],
             set_current_sound_playing: Callable[[Wave_read], None]):
        if time() - self.timeAtLastPlay <= options["Delay Before New Sound Can Play"].state:
            return
        self.timeAtLastPlay = time()
        for stream in self.streamList.streamList:
            if not stream.isPlaying:
                stream.set_wav(self.filePath)
                set_current_sound_playing(stream.wav)
                stream.playSoundThread = stream.get_play_thread(options, get_current_sound_playing)
                stream.playSoundThread.start()
                stream.isPlaying = True
                stream.timeAtLastPlay = time()
                print("Playing " + self.filePath)
                return
        print("Playing " + self.filePath)
        earliest_stream = self.streamList.stream_with_earliest_play()
        earliest_stream.set_wav(self.filePath)
        set_current_sound_playing(earliest_stream.wav)
        earliest_stream.timeAtLastPlay = time()
