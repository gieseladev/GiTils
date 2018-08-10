from motor.motor_asyncio import AsyncIOMotorClient
from vibora import Vibora

from .config import Config


def add_components(app: Vibora, config: Config):
    mongo_client = AsyncIOMotorClient(config.mongo_uri)
    mongo_db = mongo_client[config.mongo_db]

    app.components.add(config, mongo_client, mongo_db)
