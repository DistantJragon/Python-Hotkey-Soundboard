from keyboard import unhook_all
from Soundboard import Soundboard
from GUISoundboard import GUISoundboard

if __name__ == "__main__":
    s = Soundboard()
    s.add_group_file_to_group_list()
    s.start()
    w = GUISoundboard(s)
    try:
        w.window.mainloop()
    finally:
        unhook_all()
        s.stopThread = True
        # s.save_groups()
