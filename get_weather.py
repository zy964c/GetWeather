import requests
import model
import json
import time
import logging
import logging.handlers

from pprint import pprint, pformat
from threading import Thread, Event
from collections import defaultdict, abc
from actions import Settings

api_key = 'e6f1dd0f3a1cd2e234ba71bdd90e8e2d'
LOG_FILENAME = 'log'

my_logger = logging.getLogger('my_logger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=5*10**6, backupCount=5)
handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler_console.setFormatter(formatter)
my_logger.addHandler(handler)
my_logger.addHandler(handler_console)

def get_data(payload):

    r = requests.get('http://api.openweathermap.org/data/2.5/group', timeout=1,
        params=payload)   
    recieved_data = r.json()
    my_logger.debug(recieved_data)
    return recieved_data

def read_settings(fp, timeout, e):
    """
    reads settings file every "timeout" seconds
    """
    while True:
        with open(fp) as s:
            settings = json.load(s)
            old_timeout = Settings.options['refresh_period']
            if settings != Settings.options:
                Settings.update_opts(settings)
                my_logger.info('Settings updated')
                if old_timeout != Settings.options['refresh_period']:
                    e.set()
                    e.clear()
        time.sleep(timeout)

def main():

    with open('settings') as s:
            settings = json.load(s)
            Settings.update_opts(settings)
    read_cities()
    my_logger.info('cities data read complete') 
    e = Event()
    t = Thread(target=read_settings, args=('settings', 10, e,), daemon=True)
    t1 = Thread(target=main_loop, args=(e,), daemon=True)
    t.start()
    t1.start()
    t.join()
    t1.join()
    
def main_loop(e):

    while True:
        if len(Settings.options) != 0:
            cities = parse_cities(Settings.options['cities'])
            params = {'id': ','.join(cities), 'APPID': api_key}
            try:
                data_dl = get_data(params)
                if data_dl.get('cod', None) == 401:
                    raise(requests.exceptions.RequestException('api key is incorrect'))
            except requests.exceptions.RequestException:
                my_logger.exception('RequestException')
            else:
                for data_raw in data_dl['list']:
                    my_logger.debug(pformat(data_raw)) 
                    data = defaultdict(dict, data_raw)
                    data_weather_all = {'dt': data['dt'],
                                        'base': data['base'],
                                        'wind_speed': data['wind'].get('speed', {}),
                                        'wind_deg': data['wind'].get('deg', {}),
                                        'clouds_all': data['clouds'].get('all', {}),
                                        'rain_3h': data['rain'].get('3h', {}),
                                        'snow_3h': data['snow'].get('3h', {}),
                                        'cod': data['cod'],
                                        'main_temp': data['main'].get('temp', {}),
                                        'main_pressure': data['main'].get('pressure', {}),
                                        'main_humidity': data['main'].get('humidity', {}),
                                        'main_temp_min': data['main'].get('temp_min', {}),
                                        'main_temp_max': data['main'].get('temp_max', {}),
                                        'main_sea_level': data['main'].get('sea_level', {}),
                                        'main_sea_level': data['main'].get('sea_level', {}),
                                        'main_grnd_level': data['main'].get('grnd_level', {}),}

                    data_filtered = filter_input(data_weather_all)
                    model.add_record(data_filtered, data_raw)
            finally:
                e.wait(timeout=int(Settings.options['refresh_period']))
def read_cities():
    with open('city.list.json') as s:
        all_cities_data = json.load(s)
        Settings.cities.update({d['name']: str(d['id']) for d in all_cities_data})

def parse_cities(cities):
    city_ids = []
    for city in cities:
        city_ids.append(Settings.cities[city])
    return city_ids
                
def filter_input(mapping):
    empty_keys = []
    for key in mapping:
        if isinstance(mapping[key], abc.Mapping):
            if len(mapping[key]) == 0:
                empty_keys.append(key)
    for key in empty_keys:
        mapping.pop(key)
    return mapping

if __name__ == "__main__":
    main()