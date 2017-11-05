import flask

from . import constants
from .blueprints import token_provider

app = flask.Flask("GiTils")

app.register_blueprint(token_provider.blueprint)
