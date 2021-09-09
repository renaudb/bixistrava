"""Strava auth script.

Simple script to perform Strava auth.

  Script usage:

  ./.venv/bin/python3 -m bixistrava.strava \
    --client-id STRAVA_CLIENT_ID \
    --client-secret STRAVA_CLIENT_SECRET
"""

from .main import main

if __name__ == '__main__':
    main()
