from Entry import Entry


class GroupEntry:
    def __init__(self, entry: Entry, weight: int):
        self.soundEntry = entry
        self.weight = weight
