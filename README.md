# Python-Hotkey-Soundboard
(Only 64-Bit is guaranteed)
## Easy program that plays WAV files when you press a key or combination of keys.

###### Adding Sounds and Hotkeys

1. Find the device you want to use by starting "Start seeIndeciesOfDevices.bat" and replace deviceID in soundboard.py with desired device id
2. Add the WAV file to the Sounds folder
3. Add sound entries following the example sounds giving within soundboard.py (exampleSound = Entr...)
4. Start the program with "Start soundboard.bat" and cause chaos

Note: Only wave files work. Make sure sounds have a consistent sample rate and number of channels

###### Start When User Logs Into Windows

You can have this program start when you log in to Windows by either

- Creating a shortcut from Window's startup folder to "Start soundboard.bat"
or
- Using Task Scheduler to start "Start soundboard.bat" on boot
