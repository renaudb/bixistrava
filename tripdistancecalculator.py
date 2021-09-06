import logging
import requests

from bixi import Trip


class TripDistanceCalculator(object):
    def distance(self, trip: Trip) -> float:
        return self.distances([trip])[0]

    def distances(self, trips: list[Trip]) -> list[float]:
        raise NotImplementedError()


class GoogleMapsTripDistanceCalculator(TripDistanceCalculator):
    DISTANCE_MATRIX_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    def __init__(self, api_key: str):
        self._api_key = api_key

    def distances(self, trips: list[Trip]) -> list[float]:
        origins = [
            f'{t.start_station.lat},{t.start_station.lng}' for t in trips
        ]
        destinations = [
            f'{t.end_station.lat},{t.end_station.lng}' for t in trips
        ]
        r = requests.get(
            self.DISTANCE_MATRIX_URL,
            params={
                'key': self._api_key,
                'origins': '|'.join(origins),
                'destinations': '|'.join(destinations),
                'mode': 'bicycling',
            },
        )
        distances = []
        for i in range(0, len(trips)):
            el = r.json()['rows'][i]['elements'][i]
            distances.append(el['distance']['value'])
        return distances
