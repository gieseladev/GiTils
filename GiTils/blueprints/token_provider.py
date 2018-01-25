"""Tokens provider."""

from flask import Blueprint, current_app, g, jsonify
from spotipy.oauth2 import SpotifyClientCredentials

blueprint = Blueprint("Token Provider", __name__, url_prefix="/tokens")


def get_spotify_creds():
    """Get or create spotify creds object."""
    if "spotify_creds" not in g:
        g.spotify_creds = SpotifyClientCredentials(current_app.config["SPOTIFY_CLIENT_ID"], current_app.config["SPOTIFY_CLIENT_SECRET"])
    return g.spotify_creds


@blueprint.route("/spotify")
def get_spotify_token():
    """Return valid spotify token."""
    creds = get_spotify_creds()
    creds.get_access_token()
    return jsonify(creds.token_info)
