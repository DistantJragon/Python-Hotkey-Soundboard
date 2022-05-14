import pyaudio
p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numberOfDevice = info.get('deviceCount')
for i in range(0, numberOfDevice):
    print("Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
x = input('Done!')
