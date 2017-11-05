from spotipy.oauth2 import SpotifyClientCredentials

from . import constants
from .gitils import app

spotify_credentials = SpotifyClientCredentials(constants.Spotify.CLIENT_ID, constants.Spotify.CLIENT_SECRET)


@app.route("/tokens/spotify")
def get_spotify_token():
    return spotify_credentials.get_access_token()
