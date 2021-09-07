"""Strava auth utilities.

Includes functions as well as a simple script to perform Strava auth.

  Script usage:

  ./.venv/bin/python3 auth.py \
    --client-id STRAVA_CLIENT_ID \
    --client-secret STRAVA_CLIENT_SECRET
"""

import argparse
import json
import requests
import typing as t
import urllib.parse
import webbrowser

from flask import Flask, jsonify, request
from typing import Any


def _authorize_url(client_id: str,
                   redirect_uri: str,
                   response_type: str = 'code',
                   approval_prompt: str = 'auto',
                   scope: str = 'activity:read') -> str:
    url = 'https://www.strava.com/api/v3/oauth/authorize'
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': response_type,
        'approval_prompt': approval_prompt,
        'scope': scope,
    }
    return url + '?' + urllib.parse.urlencode(params)


def _token(client_id: str,
           client_secret: str,
           grant_type: str,
           code: str = None,
           refresh_token: str = None) -> requests.Response:
    url = 'https://www.strava.com/api/v3/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': grant_type,
    }
    if code is not None:
        data['code'] = code
    if refresh_token is not None:
        data['refresh_token'] = refresh_token
    return requests.post(url, data=data)


def auth(client_id: str, client_secret: str) -> requests.Response:
    """Authenticates a Strava user using the OAuth2 API. Includes a browser
    redirect. Returns the final API response including `access_token` and
    `refresh_token`.
    """
    host = '127.0.0.1'
    port = 5000
    # Open auth page in browser.
    url = _authorize_url(
        client_id=client_id,
        redirect_uri=f'http://{host}:{port}/callback',
        scope='activity:write',
    )
    webbrowser.open(url)
    # Fetch token.
    r: t.Optional[requests.Response] = None
    app = Flask(__name__)

    @app.route("/callback")
    def callback():
        nonlocal r
        r = _token(
            client_id=client_id,
            client_secret=client_secret,
            grant_type='authorization_code',
            code=request.args.get('code'),
        )
        request.environ.get('werkzeug.server.shutdown')()
        return 'Success!'

    app.run(host=host, port=port)
    # Assert token was set.
    assert r is not None
    # Return token.
    return r


def refresh(client_id: str, client_secret: str,
            refresh_token: str) -> requests.Response:
    """Refreshes a Strava `access_token` using an existing`refresh_token`.
    Returns the final API response including `access_token` and `refresh_token`.
    """
    return _token(
        client_id=client_id,
        client_secret=client_secret,
        grant_type='refresh_token',
        refresh_token=refresh_token,
    )


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


if __name__ == "__main__":
    main()
