import requests
import requests_mock

from datetime import datetime
from pytz import timezone

from bixistrava.bixi import Bixi
from test import testdata


def test_trips():
    account = 'TEST-1'
    dt = datetime(2021, 8, 24)
    ds = dt.strftime('%d/%m/%Y')
    uri = f'https://secure.bixi.com/profile/trips/{account}/print/preview?edTripsPrint%5BstartDate%5D={ds}&edTripsPrint%5BendDate%5D={ds}'
    with open(testdata.path('bixi/print.html')) as f:
        html = f.read()

    session = requests.session()
    adapter = requests_mock.Adapter()
    session.mount('https://', adapter)
    adapter.register_uri('GET', uri, text=html)

    bixi = Bixi(session, account)
    trips = bixi.trips(dt, dt)

    tz = timezone('US/Eastern')

    assert len(trips) == 2

    assert trips[0].start_dt == tz.localize(datetime(2021, 8, 24, 15, 57, 29))
    assert trips[0].end_dt == tz.localize(datetime(2021, 8, 24, 16, 18, 4))
    assert trips[0].start_station.name == 'de la Commune / Berri'
    assert trips[0].end_station.name == 'Duvernay / Charlevoix'

    assert trips[1].start_dt == tz.localize(datetime(2021, 8, 24, 15, 24, 26))
    assert trips[1].end_dt == tz.localize(datetime(2021, 8, 24, 15, 56, 40))
    assert trips[1].start_station.name == 'Chabot / Beaubien'
    assert trips[1].end_station.name == 'de la Commune / Berri'
