import unittest
import get_weather
import json

from actions import Settings
from unittest.mock import patch


get_weather.read_cities()

class TestData(unittest.TestCase):
    def setUp(self):
        with open('settings.json') as s:
            settings = json.load(s)
            Settings.update_opts(settings)
        with open('test_data.json') as t:
            self.test_data = json.load(t)

    def test_parse_cities(self):
        get_weather.read_cities()
        cities = [
        "Moskva", 
        "Novosibirsk",
        "Krasnodar"
        ]
        city_list = get_weather.parse_cities(cities)
        self.assertEqual(city_list, ['1220988', '1496747', '542420'])

    def test_main_loop(self):
        with patch('get_weather.get_data', return_value=self.test_data):
            get_weather.read_cities()
            try:
                with patch('model.add_record') as mock:
                    get_weather.main_loop('arg')
            except AttributeError:
                pass
            args, kwargs = mock.call_args
            self.assertIn('name', args[1])
            for d in args:
                self.assertNotIn('snow_3h', d)

if __name__ == "__main__":
    unittest.main()
