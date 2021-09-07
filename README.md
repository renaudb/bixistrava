Bixi to Strava Uploader
=======================

## Description

Simple script to upload Bixi rides within a time range to Strava.

## Usage

```shell
# Create venv.
python3 -m venv .venv

# Install dependencies.
./.venv/bin/pip3 install -r requirements.txt

# Run script.
./.venv/bin/python3 bixistrava.py \
  --start-date 2021-08-25 \
  --end-date 2021-09-05 \
  --bixi-username BIXI_USERNAME \
  --bixi-password BIXI_PASSWORD \
  --bixi-account BIXI_ACCOUNT \
  --googlemaps-api-key GOOGLEMAPS_API_KEY \
  --strava-client-id STRAVA_CLIENT_ID \
  --strava-client-secret STRAVA_CLIENT_SECRET