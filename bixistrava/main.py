import argparse
import logging
import sys
import os

from datetime import datetime

from .bixi import Bixi, Station, Trip
from .strava import Strava
from .tripdistancecalculator import GoogleMapsTripDistanceCalculator


def _main(start: datetime, end: datetime, bixi_username: str,
          bixi_password: str, bixi_account: str, googlemaps_api_key: str,
          strava_client_id: str, strava_client_secret: str):
    logging.info('Connecting to Bixi.')
    bixi = Bixi.login(bixi_username, bixi_password, bixi_account)
    logging.info('Connected to Bixi.')

    logging.info(f'Fetching trips from {start} to {end}')
    trips = bixi.trips(start, end)
    logging.info(f'Fetched {len(trips)} trips')
    for t in trips:
        logging.debug(f'Trip: {t}')

    if not trips:
        sys.exit(0)

    logging.info('Calculating distances using Google Maps')
    calc = GoogleMapsTripDistanceCalculator(googlemaps_api_key)
    distances = calc.distances(trips)
    logging.info(f'Calculated {len(distances)} distances')
    for d in distances:
        logging.debug(f'Distance: {d}')

    logging.info('Connecting to Strava')
    strava = Strava.auth(strava_client_id, strava_client_secret)
    logging.info('Connected to Strava')

    logging.info('Creating activities')
    for (t, d) in zip(trips, distances):
        r = strava.create_activity(
            name='Bixi Ride',
            type='Ride',
            start_date_local=t.start_dt,
            elapsed_time=int(t.duration.total_seconds()),
            description=
            f'Bixi ride from {t.start_station.name} to {t.end_station.name}',
            distance=d,
            commute=True,
        )
        logging.debug(f'Created activity: {r.json()}')
    logging.info('Created activities')


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Upload Bixi activities to Strava.')
    # Start/end dates.
    parser.add_argument(
        '--start-date',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        required=True,
    )
    parser.add_argument(
        '--end-date',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        required=True,
    )
    # Bixi arguments.
    parser.add_argument(
        '--bixi-username',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--bixi-password',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--bixi-account',
        type=str,
        required=True,
    )
    # Google maps arguments.
    parser.add_argument(
        '--googlemaps-api-key',
        type=str,
        required=True,
    )
    # Strava arguments.
    parser.add_argument(
        '--strava-client-id',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--strava-client-secret',
        type=str,
        required=True,
    )
    return parser.parse_args()


def main():
    """CLI script entrypoint."""
    logging.basicConfig(
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )

    args = _get_args()
    _main(args.start_date, args.end_date, args.bixi_username,
          args.bixi_password, args.bixi_account, args.googlemaps_api_key,
          args.strava_client_id, args.strava_client_secret)


def cloudfn():
    start = datetime.today()
    end = datetime.today()

    bixi_username = os.environ.get('BIXI_USERNAME')
    if not bixi_username:
        raise ValueError('Missing Bixi username')
    bixi_password = os.environ.get('BIXI_PASSWORD')
    if not bixi_password:
        raise ValueError('Missing Bixi password')
    bixi_account = os.environ.get('BIXI_ACCOUNT')
    if not bixi_account:
        raise ValueError('Missing Bixi account')
    googlemaps_api_key = os.environ.get('GOOGLEMAPS_API_KEY')
    if not googlemaps_api_key:
        raise ValueError('Missing Google Maps API key')
    strava_client_id = os.environ.get('STRAVA_CLIENT_ID')
    if not strava_client_id:
        raise ValueError('Missing Strava client id')
    strava_client_secret = os.environ.get('STRAVA_CLIENT_SECRET')
    if not strava_client_secret:
        raise ValueError('Missing Strava client secret')

    _main(start, end, bixi_username, bixi_password, bixi_account,
          googlemaps_api_key, strava_client_id, strava_client_secret)


if __name__ == "__main__":
    main()
