import os

import numpy as np
import requests
from typing import Optional
from urllib.parse import quote


class GooglePlaceApi:
    def __init__(self):
        self.API_TYPE = 'textsearch' # findplacefromtext
        self.url = f"https://maps.googleapis.com/maps/api/place/{self.API_TYPE}/json"
        self.google_api_key = os.getenv('GOOGLE_API_KEY')

    def shareble_link(self, lat, lng):
        # maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        location_param = quote(f'{lat},{lng}')
        maps_url =  f"https://www.google.com/maps?q={location_param}"
        return maps_url

    def shareble_link_pretty(self, item):
        """ATTENTION: do NOT use to avoid additional payments, x2"""
        place_id =  item['place_id']
        fields = quote('name,url')

        params = {
            "place_id": place_id,
            "fields": fields,
            "key": self.google_api_key
        }
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        headers = {}
        response = requests.get(url, params=params, headers=headers).json()['result']

        return response

    def api_request(self, q: str, lat_lng: Optional[str]):
        if lat_lng is None:
            lat, lng = 34.707130,33.022617  # Lemesos city centre
        else:
            lat, lng = lat_lng.split(',')
        radius = 5000
        
        params = {
            "inputtype": "textquery",
            "fields": "formatted_address,name,place_id",
            "key": self.google_api_key
        }
        if self.API_TYPE == 'findplacefromtext':
            location = f'circle:{radius}@{lat},{lng}'
            params.update({"locationbias": location, "input": q})
        else:
            location_param = f'{lat},{lng}'
            params.update({"location": location_param, 'radius': radius, "query": q})

        headers = {}
        response = requests.get(self.url, params=params, headers=headers).json()
        if self.API_TYPE == 'findplacefromtext':
            response = response['candidates']
        else:
            response = response['results']
        return response

    def get_recs(self, location: str, q = "Beer bar, pub"):
        response = self.api_request(q, lat_lng=location)
        candidates = []
        for item in response:
            share_link = self.shareble_link(**item['geometry']['location']) # or shareble_link_pretty(item)
            place = {'name': item['name'], 'link': share_link}
            candidates.append(place)
        res_link = None
        if len(candidates) > 0:
            res_link = np.random.choice(candidates)
        else:
            print('ERROR: failed to recomend %s', q)
        return res_link

    def find_place(self, place_name: str):
        print('place_name %s' % place_name)
        params = {
            "address": place_name,
            "key": self.google_api_key
        }
        url = f'https://maps.googleapis.com/maps/api/geocode/json'
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            print(f'Latitude: {latitude}, Longitude: {longitude}')
        else:
            print('Geocoding failed')
        return f'{latitude},{longitude}'

place_recommender = GooglePlaceApi()
