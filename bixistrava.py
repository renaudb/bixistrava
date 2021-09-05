#!/usr/bin/python3

import argparse
import logging
import os

from datetime import datetime

from bixi import Bixi, Station, Trip
from tripdistancecalculator import GoogleMapsTripDistanceCalculator

def _get_args():
    parser = argparse.ArgumentParser(description='Upload Bixi activities to Strava.')
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
    return parser.parse_args()

def main():
    logging.basicConfig(
        encoding = 'utf-8',
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level = logging.DEBUG,
    )

    args = _get_args()
    username = args.bixi_username
    if not username:
        raise ValueError('Missing USERNAME')
    password = args.bixi_password
    if not password:
        raise ValueError('Missing PASSWORD')
    account = args.bixi_account
    if not account:
        raise ValueError('Missing ACCOUNT')
    googlemaps_api_key = args.googlemaps_api_key
    if not googlemaps_api_key:
        raise ValueError('Missing GOOGLEMAPS_API_KEY')

    start = datetime(2021, 8, 24)
    end = datetime(2021, 8, 24)

    logging.info('Connecting to Bixi.')
    bixi = Bixi(username, password, account)
    logging.info('Connected to Bixi.')

    logging.info(f'Fetching trips from {start} to {end}')
    trips = bixi.trips(start, end)
    logging.info(f'Fetched {len(trips)} trips')
    for t in trips: logging.debug(f'Trip: {t}')

    logging.info('Calculating distances using Google Maps')
    calc = GoogleMapsTripDistanceCalculator(googlemaps_api_key)
    distances = calc.distances(trips)
    logging.info(f'Calculated {len(distances)} distances')
    for d in distances: logging.debug(f'Distance: {d}')

main()
