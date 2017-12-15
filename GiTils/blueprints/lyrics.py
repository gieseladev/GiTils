"""Lyrics endpoint."""

from flask import Blueprint, jsonify

from ..lyrics import search_for_lyrics

blueprint = Blueprint("lyrics", "GiTils")


@blueprint.route("/lyrics/<query>")
def get_lyrics(query):
    """Return lyrics for query."""
    lyrics = search_for_lyrics(query)
    return jsonify(lyrics)
