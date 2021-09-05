import logging
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse

class Station(object):
    def __init__(self, id: str, name: str, lat: float, lng: float):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng

    def __repr__(self) -> str:
        return f'Station([{self.id}, {self.name}, {self.lat}, {self.lng}])'

class Trip(object):
    def __init__(self, start_dt: datetime, start_station: Station, end_dt: datetime, end_station: Station):
        self.start_dt = start_dt
        self.start_station = start_station
        self.end_dt = end_dt
        self.end_station = end_station

    def duration(self) -> timedelta:
        self.end_dt - self.start_dt

    def __repr__(self) -> str:
        return f'Trip([{self.start_dt}, {self.start_station}, {self.end_dt}, {self.end_station}])'

class Bixi(object):
    LOGIN_URL = 'https://secure.bixi.com/profile/login'
    LOGIN_CHECK_URL = 'https://secure.bixi.com/profile/login_check'
    TRIPS_URL = 'https://secure.bixi.com/profile/trips'
    STATIONS_URL = 'https://gbfs.velobixi.com/gbfs/en/station_information.json'

    def __init__(self, username: str, password: str, account: str):
        self._account = account
        self._session = self._login(username, password)

    def _login(self, username, password) -> requests.Session:
        # Start session
        with requests.Session() as session:
            # Get hidden inputs.
            r = session.get(self.LOGIN_URL)
            soup = BeautifulSoup(r.text, 'html.parser')
            form = soup.find(id = 'loginPopupId')
            hidden = form.find_all('input', attrs = { 'type' : 'hidden' })
            # Get auth cookie.
            data = {
                '_username' : username,
                '_password' : password,
                **{h['name'] : h['value']  for h in hidden}
            }
            r = session.post(self.LOGIN_CHECK_URL, data = data)
            return session

    def trips(self, start: datetime, end: datetime) -> list[Trip]:
        stations_by_name = {s.name: s for s in self.stations()}
        r = self._session.get(
            f'{self.TRIPS_URL}/{self._account}/print/preview',
            params = {
                'edTripsPrint[startDate]' : start.strftime('%d/%m/%Y'),
                'edTripsPrint[endDate]' : end.strftime('%d/%m/%Y'),
            }
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        body = soup.find('tbody', class_ = 'ed-html-table__items')
        rows = body.find_all('tr')
        trips = []
        for i in range(0, len(rows) - 1, 2):
            trips.append(self._parse_trip_rows(rows[i], rows[i + 1], stations_by_name))
        return trips

    def _parse_trip_rows(self, start, end, stations: dict[str, Station]) -> Trip:
        INFO_PREFIX = 'ed-html-table__item__info_trip-'
        s_ds = start.find(class_ = INFO_PREFIX + 'start-date').contents[1].strip()
        s_dt = datetime.strptime(s_ds, '%d/%m/%Y %H:%M:%S')
        s_station_name = start.find(class_ = INFO_PREFIX + 'start-station').text.strip()
        s_station = stations[s_station_name]
        if not s_station:
            logging.error(f'Missing start station: {s_station_name}')
        e_ds = end.find(class_ = INFO_PREFIX + 'end-date').contents[1].strip()
        e_dt = datetime.strptime(e_ds, '%d/%m/%Y %H:%M:%S')
        e_station_name = end.find(class_ = INFO_PREFIX + 'end-station').text.strip()
        e_station = stations[e_station_name]
        if not e_station:
            logging.error(f'Missing end station: {e_station_name}')
        return Trip(s_dt, s_station, e_dt, e_station)

    def stations(self) -> list[Station]:
        r = requests.get(self.STATIONS_URL)
        data = r.json()
        return [
            Station(s['station_id'], s['name'], s['lat'], s['lon'])
            for s in data['data']['stations']
        ]
