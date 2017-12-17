"""Lyrics endpoint."""

import json
import logging
from os import path

import lyricsfinder
from lyricsfinder import utils

from flask import Blueprint, jsonify

from ..constants import FileLocations, Google, Static

log = logging.getLogger(__name__)


blueprint = Blueprint("lyrics", "GiTils")

lyrics_folder = path.join(Static.ROOT, FileLocations.LYRICS)


def load_cached(query):
    """Try to load lyrics for query from the cache."""
    filename = utils.safe_filename(query)
    file_path = path.join(lyrics_folder, filename)

    if path.isfile(file_path):
        log.info("cached lyrics for \"{}\"".format(query))

        with open(file_path, "r") as f:
            data = json.load(f)
            return lyricsfinder.models.Lyrics.from_dict(data)
    else:
        return False


@blueprint.route("/lyrics/<query>")
def get_lyrics(query):
    """Return lyrics for query."""
    lyrics = load_cached(query)

    if not lyrics:
        lyrics = lyricsfinder.search_lyrics(query, google_api_key=Google.API_KEY)
        with open(path.join(lyrics_folder, lyrics.save_name), "w+") as f:
            log.info("saved lyrics {} to cache".format(lyrics))
            lyrics.save(f)

    return jsonify(lyrics.to_dict())
