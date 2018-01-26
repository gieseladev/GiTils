"""Lyrics endpoint."""

import logging

import lyricsfinder
from flask import Blueprint, current_app, jsonify
from lyricsfinder.utils import safe_filename

from GiTils.gitils import mongo_database

log = logging.getLogger(__name__)


blueprint = Blueprint("Lyrics", __name__)


@blueprint.route("/lyrics/<query>")
def get_lyrics(query):
    """Return lyrics for query."""
    coll = mongo_database.lyrics
    lyrics_data = coll.find_one({"filename": safe_filename(query)})

    if not lyrics_data:
        lyrics = lyricsfinder.search_lyrics(query, google_api_key=current_app.config["GOOGLE_API_KEY"])
        lyrics_data = lyrics.to_dict()
        lyrics_data["filename"] = lyrics.save_name
        log.debug(f"saved lyrics for query {query}")
        coll.insert_one(lyrics_data)

    lyrics = {
        "title": lyrics_data["title"],
        "lyrics": lyrics_data["lyrics"],
        "origin": lyrics_data["origin"],
        "timestamp": lyrics_data["timestamp"]
    }
    return jsonify(lyrics)
