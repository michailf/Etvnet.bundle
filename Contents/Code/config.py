import json
import os

class Config:
    def __init__(self, config_name):
        self.config_name = config_name
        self.data = {}

    def get_value(self, name):
        if name in self.data.keys():
            return self.data[name]
        else:
            return None

    def load(self):
        self.data.clear()

        if os.path.isfile(self.config_name):
            with open(self.config_name, 'r') as file:
                self.data = json.load(file)

    def save(self, data=None):
        if data:
            self.data = data

        with open(self.config_name, 'w') as file:
            json.dump(self.data, file, indent=4)