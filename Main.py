from keyboard import unhook_all
from threading import Thread
from Soundboard import Soundboard, get_name_of_device
from SoundboardMenuing import soundboard_menu

if __name__ == "__main__":
    s = Soundboard()
    s.create_all_groups()
    print("Using " + get_name_of_device(s.options["Device"].state) + " device")

    if s.options["Poll For Keyboard"].state:
        keepRunningThread = Thread(target=s.keep_program_running_poll)
        keepRunningThread.start()
    else:
        s.hook_hotkeys()
    print("Ready!")
    soundboard_menu(s)
    s.userWantsToQuit = True
    unhook_all()
