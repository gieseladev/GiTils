"""Main entry point for the server."""

import importlib

from flask import Flask, g
from pymongo import MongoClient
from werkzeug.local import LocalProxy

app = Flask(__name__)
app.config.from_object(f"{__package__}.default_config")
app.config.from_envvar("GITILS_SETTINGS")


def get_mongo():
    """Get or create the Mongo client."""
    if "mongo_client" not in g:
        g.mongo_client = MongoClient(app.config["MONGODB_URI"])
    return g.mongo_client


def get_mongo_database():
    """Get the database."""
    return get_mongo()[__package__]


mongo_client = LocalProxy(get_mongo)
mongo_database = LocalProxy(get_mongo_database)


@app.teardown_appcontext
def close_mongo(exception):
    """Clean closing for MongoDB."""
    if "mongo_client" in g:
        g.mongo_client.close()


for bp in app.config["ACTIVE_BLUEPRINTS"]:
    module = importlib.import_module(f"{__package__}.blueprints.{bp}")
    app.register_blueprint(module.blueprint)
