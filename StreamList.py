from pyaudio import PyAudio
from wave import Wave_read
from Stream import Stream


class StreamList:
    def __init__(self,
                 template_wav: Wave_read,
                 number_of_streams: int,
                 device_index: int):
        self.format = PyAudio().get_format_from_width(template_wav.getsampwidth())
        self.channels = template_wav.getnchannels()
        self.rate = template_wav.getframerate()
        self.streamList = []
        for i in range(number_of_streams):
            self.streamList.append(Stream(device_index, self.format, self.channels, self.rate))

    def stream_with_earliest_play(self):
        earliest_stream = self.streamList[0]
        for stream in self.streamList:
            if stream.timeAtLastPlay < earliest_stream.timeAtLastPlay:
                earliest_stream = stream
        return earliest_stream
