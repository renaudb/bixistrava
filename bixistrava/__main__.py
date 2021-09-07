"""Simple script to upload Bixi rides within a time range to Strava.

Fetches rides within a time range from Bixi, computes distances between stations
using Google Maps and uploads the result to Strava.

  Script usage:

  ./.venv/bin/python3 -m bixistrava \
    --start-date 2021-08-25 \
    --end-date 2021-09-05 \
    --bixi-username BIXI_USERNAME \
    --bixi-password BIXI_PASSWORD \
    --bixi-account BIXI_ACCOUNT \
    --googlemaps-api-key GOOGLEMAPS_API_KEY \
    --strava-client-id STRAVA_CLIENT_ID \
    --strava-client-secret STRAVA_CLIENT_SECRET
"""

from .main import main

if __name__ == '__main__':
    main()
