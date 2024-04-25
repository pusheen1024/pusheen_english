import random

import requests

from config import YANDEX_MAPS


class MapsAPI:
    def __init__(self):
        self.api_server = "http://static-maps.yandex.ru/1.x/"
        self.geocoder_server = "http://geocode-maps.yandex.ru/1.x/"
        self.type = 'sat'
    
    def search_by_coords(self, lon, lat, new_search=True):
        self.params = {'l': self.type,
                       'll': ','.join([str(lon), str(lat)]),
                       'z': 13}
        response = requests.get(self.api_server, params=self.params)
        return response.content

    def search_by_name(self, object_name):
        geocoder_params = {'apikey': YANDEX_MAPS,
                           'geocode': object_name,
                           'format': 'json'}
        response = requests.get(self.geocoder_server, params=geocoder_params).json()
        toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        lon_1, lat_1 = map(float, toponym["boundedBy"]["Envelope"]["lowerCorner"].split())
        lon_2, lat_2 = map(float, toponym["boundedBy"]["Envelope"]["upperCorner"].split())
        lon, lat = random.uniform(lon_1, lon_2), random.uniform(lat_1, lat_2)
        return self.search_by_coords(lon, lat)
