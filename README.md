# Python-Hotkey-Soundboard
(Only 64-bit Windows will work with the program provided in the releases tab.
Other OS's will need to download this program and its dependencies )
## Easy program that plays .wav files when you press a key or combination of keys.

### Sound Groups and the Group Chooser

- All sounds need to be in some group, even if by themselves. Create a new group by entering a name for your new group
in the Group Chooser and press enter (or click the + button).  
- Existing groups can be edited by typing its name in the group chooser or selecting its name
from the dropdown box and pressing enter.

### The Group Editor

- Multiple groups can be in the editor at the same time
- The group's name can be changed simply by typing a new name in its nametag. 
  - Be careful not to have groups with duplicate names! You may lose a group after a program restart.
- A group can be returned to the group chooser via its back arrow or deleted by double-clicking its trash button
- The group's sounds live in the bottom left box of the group.
  - New .wav files or directories[^1] with .wav files can be dragged and dropped from the file explorer to the box.[^2]
    - The path of the file/directory and number of files in the directory can be seen by hovering over its name with the cursor
  - Sound files/directories can be moved by clicking on their name and pressing up or down on the keyboard.
    - If the group does not play randomly, the soundboard will play the files/directories in the order shown in the soundboard
  - Each sound file/directory has a weight
    - If the group does play randomly, the soundboard will play the files/directories at random, with heavier sounds having a higher chance at being played
- The group's hotkeys live in the bottom-right box of the group.
  - Hotkeys can be added by pressing the plus button at the bottom of the hotkey list.

### Options
Each option gives context when hovering over the option name with the cursor

### Start When The User Logs Into Windows

You can have this program start when you log in to Windows via one of these methods:
- Creating a shortcut from Window's startup folder to "Start soundboard.bat"
- Using the Task Scheduler program to start "Start soundboard.bat" on boot

[^1]: Folders will be referred to as directories  
[^2]: The soundboard won't know where a sound file/directory is if it is moved to a different directory.  
  If you move a sound file/directory while the program is closed, you must delete the old file/directory
  from the soundboard and replace it

