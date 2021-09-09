import argparse
import logging
import sys
import typing as t

from datetime import datetime

from .bixi import Bixi, Station, Trip
from .strava import Strava
from .tripdistancecalculator import GoogleMapsTripDistanceCalculator


def _main(start: datetime,
          end: datetime,
          bixi_username: str,
          bixi_password: str,
          bixi_account: str,
          googlemaps_api_key: str,
          strava_client_id: str,
          strava_client_secret: str,
          strava_refresh_token: str = None) -> t.Optional[str]:
    # Log into Bixi.
    logging.info('Connecting to Bixi.')
    bixi = Bixi.login(bixi_username, bixi_password, bixi_account)
    logging.info('Connected to Bixi.')

    # Fetch trips.
    logging.info(f'Fetching trips from {start} to {end}')
    trips = bixi.trips(start, end)
    logging.info(f'Fetched {len(trips)} trips')
    for t in trips:
        logging.debug(f'Trip: {t}')

    # If no trips where fetched, return early.
    if not trips:
        logging.info(f'No trips fetched, ending early.')
        return None

    # Compute distances for all trips.
    logging.info('Calculating distances using Google Maps')
    calc = GoogleMapsTripDistanceCalculator(googlemaps_api_key)
    distances = calc.distances(trips)
    logging.info(f'Calculated {len(distances)} distances')
    for d in distances:
        logging.debug(f'Distance: {d}')

    # Log into Strava.
    logging.info('Connecting to Strava')
    if strava_refresh_token:
        strava = Strava.refresh(strava_client_id, strava_client_secret,
                                strava_refresh_token)
    else:
        strava = Strava.auth(strava_client_id, strava_client_secret)
    logging.info('Connected to Strava')

    # Create activities.
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

    return strava.refresh_token


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
    parser.add_argument(
        '--strava-refresh-token',
        type=str,
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
    strava_refresh_token = _main(args.start_date, args.end_date,
                                 args.bixi_username, args.bixi_password,
                                 args.bixi_account, args.googlemaps_api_key,
                                 args.strava_client_id,
                                 args.strava_client_secret,
                                 args.strava_refresh_token)
    if strava_refresh_token:
        print(f'Strava refresh token: {strava_refresh_token}')


if __name__ == "__main__":
    main()
