import test_helper

import unittest
import json

from radio_service import RadioService

class RadioServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = RadioService()

    def test_get_stations(self):
        result = self.service.get_stations()

        print(json.dumps(result, indent=4))

    def test_get_station(self):
        result = self.service.get_station(36)

        print(json.dumps(result, indent=4))

if __name__ == '__main__':
    unittest.main()