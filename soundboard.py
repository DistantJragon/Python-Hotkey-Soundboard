import pyaudio
import wave
import sys

chunk = 1024
filename = "Sounds/ricardo boink.wav"
waveFile = wave.open(filename, 'rb')

portAuidoInterface = pyaudio.PyAudio()
stream = portAuidoInterface.open(
    format = portAuidoInterface.get_format_from_width(waveFile.getsampwidth()),
    channels = waveFile.getnchannels(),
    rate = waveFile.getframerate(),
    output = True)
data = waveFile.readframes(chunk)
while data != b'':
    stream.write(data)
    data = waveFile.readframes(chunk)

stream.close()
portAuidoInterface.terminate()