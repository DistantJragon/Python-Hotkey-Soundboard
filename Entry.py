from time import time
from typing import Callable, Optional
from wave import open, Wave_read
from StreamList import StreamList
from Option import Option


class Entry:
    def __init__(self,
                 file_name: str,
                 get_stream_list: Callable[[Wave_read], StreamList]):
        self.filePath = 'Sounds/' + file_name
        self.wav = open(self.filePath, 'rb')
        self.streamList = get_stream_list(self.wav)

    def play(self,
             options: dict[str, Option],
             get_current_sound_playing: Callable[[], Optional[Wave_read]],
             set_current_sound_playing: Callable[[Wave_read], None],
             are_all_sounds_stopped: Callable[[], bool]):
        for stream in self.streamList.streamList:
            if not stream.isPlaying:
                stream.set_wav(self.filePath)
                set_current_sound_playing(stream.wav)
                stream.playSoundThread = stream.get_play_thread(options,
                                                                get_current_sound_playing,
                                                                are_all_sounds_stopped)
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
