class Option:
    def __init__(self, json_name, json_details):
        self.name = json_name
        self.description = json_details["description"]
        self.state = json_details["state"]
