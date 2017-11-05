from flask import Blueprint
from spotipy.oauth2 import SpotifyClientCredentials

from .. import constants

blueprint = Blueprint("token_provider", "GiTils", url_prefix="/tokens")


spotify_credentials = SpotifyClientCredentials(constants.Spotify.CLIENT_ID, constants.Spotify.CLIENT_SECRET)


@blueprint.route("/spotify")
def get_spotify_token():
    return spotify_credentials.get_access_token()
