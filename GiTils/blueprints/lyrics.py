from flask import Blueprint, jsonify

from .. import constants
from ..lyrics import search_for_lyrics

blueprint = Blueprint("lyrics", "GiTils")


@blueprint.route("/lyrics/<query>")
def get_lyrics(query):
    lyrics = search_for_lyrics(query)
    return jsonify(lyrics)
