# Python-Hotkey-Soundboard
(Only 64-bit OS is guaranteed to work with this program)
## Easy program that plays WAV files when you press a key or combination of keys.

### Changing Device

1. Find the device you want to use by starting "Start seeIndicesOfDevices" (or "Start seeIndicesOfDevices.bat")
2. Replace the state of "Device" in optionsList.json with the desired device id


### Adding Sounds and Hotkeys

1. Add the WAV file to the Sounds folder
2. Add sound entries in groupList.json following the example sounds given
3. Start the program with "Start soundboard.bat"

Note: Only files ending in .wav will be recognized

### Start When The User Logs Into Windows

You can have this program start when you log in to Windows via one of these methods:
- Creating a shortcut from Window's startup folder to "Start soundboard.bat"

- Using the Task Scheduler program to start "Start soundboard.bat" on boot
