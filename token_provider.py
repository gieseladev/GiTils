import constants
from gitils import app
from spotipy.oauth2 import SpotifyClientCredentials

spotify_credentials = SpotifyClientCredentials(constants.Spotify.CLIENT_ID, constants.Spotify.CLIENT_SECRET)


@app.route("/tokens/spotify")
def get_spotify_token():
    return spotify_credentials.get_access_token()
