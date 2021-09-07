import requests

from datetime import datetime
from typing import Any

from strava.auth import auth, refresh


class StravaAuth(requests.auth.AuthBase):
    """AuthBase class adding the `access_token` Bearer Auth to a request."""
    def __init__(self, access_token: str):
        self.access_token = access_token

    def __call__(self,
                 r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["Authorization"] = "Bearer " + self.access_token
        return r


class Strava(object):
    API_URL = 'https://www.strava.com/api/v3/'

    def __init__(self, access_token: str, refresh_token: str = ''):
        self.access_token = access_token
        self.refresh_token = refresh_token

    @classmethod
    def auth(cls, client_id: str, client_secret: str) -> 'Strava':
        """Creates an authenticated Strava client through a browser
        redirect.
        """
        r = auth(client_id, client_secret)
        data = r.json()
        return cls(data['access_token'], data['refresh_token'])

    @classmethod
    def refresh(cls, client_id: str, client_secret: str,
                refresh_token: str) -> 'Strava':
        """Creates an authenticated Strava client by refreshing a
        `refresh_token`.
        """
        r = refresh(client_id, client_secret, refresh_token)
        data = r.json()
        return cls(data['access_token'], data['refresh_token'])

    def _auth(self) -> StravaAuth:
        return StravaAuth(self.access_token)

    def create_activity(self,
                        name: str,
                        type: str,
                        start_date_local: datetime,
                        elapsed_time: int,
                        description: str = '',
                        distance: float = 0.0,
                        trainer: bool = False,
                        commute: bool = False) -> requests.Response:
        """Creates an activity on Strava."""
        data = {
            'name': name,
            'type': type,
            'start_date_local': start_date_local.isoformat(),
            'elapsed_time': elapsed_time,
        }
        if description:
            data['description'] = description
        if distance:
            data['distance'] = distance
        if trainer:
            data['trainer'] = 1
        if commute:
            data['commute'] = 1

        return requests.post(self.API_URL + 'activities',
                             data=data,
                             auth=self._auth())
