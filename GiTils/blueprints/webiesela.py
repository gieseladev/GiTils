"""Webiesela manager."""

import logging

from flask import Blueprint, jsonify

from GiTils.gitils import mongo_database

log = logging.getLogger(__name__)


blueprint = Blueprint("Webiesela", __name__, url_prefix="/webiesela")
