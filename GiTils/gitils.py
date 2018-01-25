"""Main entry point for the server."""

import importlib

from flask import Flask
from pymongo import MongoClient

ACTIVE_BLUEPRINTS = ["token_provider", "lyrics"]

app = Flask(__name__)
app.config.from_object(f"{__package__}.default_config")
app.config.from_envvar("GITILS_SETTINGS")

mongo_client = MongoClient(app.config["MONGODB_URI"])
mongo_database = mongo_client[__package__]


for bp in ACTIVE_BLUEPRINTS:
    module = importlib.import_module(f"{__package__}.blueprints.{bp}")
    app.register_blueprint(module.blueprint)
