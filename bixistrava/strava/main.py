import argparse
import json

from .auth import auth


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Authenticate with Strava.')
    parser.add_argument(
        '--client-id',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--client-secret',
        type=str,
        required=True,
    )
    return parser.parse_args()


def main():
    """Simple script to fetch and print a Strava `access_token`."""
    args = _get_args()
    r = auth(args.client_id, args.client_secret)
    print(json.dumps(r.json(), sort_keys=True, indent=4))
