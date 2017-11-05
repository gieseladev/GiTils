import flask
import flask_cors

from . import constants
from .blueprints import token_provider

app = flask.Flask("GiTils")

flask_cors.CORS(app)

app.register_blueprint(token_provider.blueprint)
