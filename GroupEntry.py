class GroupEntry:
    def __init__(self, entry, weight):
        self.soundEntry = entry
        self.exists = entry.exists
        self.weight = weight if entry.exists else 0
        self.name = entry.name
        self.filePath = entry.filePath

    def play(self):
        if self.exists:
            self.soundEntry.play()

    def refresh_stream_list(self):
        self.soundEntry.refresh_stream_list()
