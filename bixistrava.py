#!/usr/bin/python3

import argparse
import logging
import os

from datetime import datetime

from bixi import Bixi, Station, Trip
from strava import Strava
from tripdistancecalculator import GoogleMapsTripDistanceCalculator


def _get_args():
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
        default=os.environ.get('BIXI_USER'),
    )
    parser.add_argument(
        '--bixi-password',
        type=str,
        default=os.environ.get('BIXI_PASS'),
    )
    parser.add_argument(
        '--bixi-account',
        type=str,
        default=os.environ.get('BIXI_ACCOUNT'),
    )
    # Google maps arguments.
    parser.add_argument(
        '--googlemaps-api-key',
        type=str,
        default=os.environ.get('GOOGLEMAPS_API_KEY'),
    )
    # Strava arguments.
    parser.add_argument(
        '--strava-client-id',
        type=str,
        default=os.environ.get('STRAVA_CLIENT_ID'),
    )
    parser.add_argument(
        '--strava-client-secret',
        type=str,
        default=os.environ.get('STRAVA_CLIENT_SECRET'),
    )
    return parser.parse_args()


def main():
    logging.basicConfig(
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )

    args = _get_args()
    username = args.bixi_username
    if not username:
        raise ValueError('Missing Bixi username')
    password = args.bixi_password
    if not password:
        raise ValueError('Missing Bixi password')
    account = args.bixi_account
    if not account:
        raise ValueError('Missing Bixi account')
    googlemaps_api_key = args.googlemaps_api_key
    if not googlemaps_api_key:
        raise ValueError('Missing Google Maps API key')
    strava_client_id = args.strava_client_id
    if not strava_client_id:
        raise ValueError('Missing Strava client id')
    strava_client_secret = args.strava_client_secret
    if not strava_client_secret:
        raise ValueError('Missing Strava client secret')

    start = args.start_date
    end = args.end_date

    logging.info('Connecting to Bixi.')
    bixi = Bixi(username, password, account)
    logging.info('Connected to Bixi.')

    logging.info(f'Fetching trips from {start} to {end}')
    trips = bixi.trips(start, end)
    logging.info(f'Fetched {len(trips)} trips')
    for t in trips:
        logging.debug(f'Trip: {t}')

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


if __name__ == "__main__":
    main()
