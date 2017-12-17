"""Lyrics endpoint."""

from flask import Blueprint, jsonify
from lyrics import search_lyrics

from ..constants import Google

blueprint = Blueprint("lyrics", "GiTils")


@blueprint.route("/lyrics/<query>")
def get_lyrics(query):
    """Return lyrics for query."""
    lyrics_data = search_lyrics(query, google_api_key=Google.API_KEY)

    return jsonify(lyrics_data.to_dict())
