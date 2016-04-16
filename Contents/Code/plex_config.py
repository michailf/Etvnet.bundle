import json
import time

from config import Config

class PlexConfig(Config):
    def load(self):
        self.data.clear()

        if Core.storage.file_exists(self.config_name):
            self.data = json.loads(str(Core.storage.load(self.config_name)))

    def save(self, data=None):
        if data:
            for key, val in data.items():
                self.data[key] = val

        if 'expires_in' in self.data:
            self.data['expires'] = int(time.time()) + int(self.data['expires_in'])

        Core.storage.save(self.config_name, json.dumps(self.data, indent=4))
