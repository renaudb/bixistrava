import requests

class Strava(object):
    def __init__(self, token: str):
        self._token = token
