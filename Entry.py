from time import time
from wave import open


class Entry:
    def __init__(self,
                 sb,
                 file_path: str):
        self.soundboard = sb
        self.filePath = file_path
        self.name = file_path.replace("/", "\\").split("\\")[-1][:-4]
        try:
            self.wav = open(file_path, 'rb')
        except FileNotFoundError:
            self.exists = False
        else:
            self.exists = True
        self.streamList = None
        self.refresh_stream_list()

    def play(self):
        if not self.exists:
            return
        for stream in self.streamList:
            if not stream.isPlaying:
                stream.set_wav(self.filePath)
                self.soundboard.currentSoundPlaying = stream.wav
                stream.playSoundThread = stream.get_play_thread()
                stream.playSoundThread.start()
                stream.isPlaying = True
                stream.timeAtLastPlay = time()
                return
        earliest_stream = self.stream_with_earliest_play()
        earliest_stream.set_wav(self.filePath)
        self.soundboard.currentSoundPlaying = earliest_stream.wav
        earliest_stream.timeAtLastPlay = time()

    def stream_with_earliest_play(self):
        earliest_stream = self.streamList[0]
        for stream in self.streamList:
            if stream.timeAtLastPlay < earliest_stream.timeAtLastPlay:
                earliest_stream = stream
        return earliest_stream

    def refresh_stream_list(self):
        if self.exists:
            self.streamList = self.soundboard.find_or_create_stream_list_from_wav(self.wav)
