import flask
import flask_cors

from . import constants
from .blueprints import lyrics, token_provider

app = flask.Flask("GiTils")
constants.Static.APP = app

flask_cors.CORS(app)

app.register_blueprint(token_provider.blueprint)
