import unittest
from get_weather import parse_cities, read_cities
from actions import Settings

class TestData(unittest.TestCase):
    
    def test_parse_cities(self):
        read_cities()
        cities = [
        "Moskva", 
        "Novosibirsk",
        "Krasnodar"
        ]
        city_list = parse_cities(cities)
        self.assertEqual(city_list, ['1220988', '1496747', '542420'])

if __name__ == "__main__":
    unittest.main()
