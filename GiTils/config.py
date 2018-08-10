import os
import typing
from ast import literal_eval
from contextlib import suppress
from typing import Any, List


def get_env_value(key: str) -> Any:
    value = os.getenv(key)
    if value:
        with suppress(SyntaxError):
            return literal_eval(value)

        with suppress(SyntaxError):
            return literal_eval(f"\"{value}\"")

    raise KeyError(f"key {key} not in env variables")


class Config:
    HOST: str = "0.0.0.0"
    PORT: int = 80

    WORKER_AMOUNT: int = None

    WEBIESELA_PORT: int = 8000
    WEBIESELA_WEBSOCKET_TIMEOUT: int = 5
    WEBIESELA_REGTOKEN_LENGTH: int = 6

    active_blueprints: List[str] = ["lyrics", "tokens"]
    mongo_uri: str = "mongodb://localhost:27017/"
    mongo_db: str = "GiTils"

    google_api_key: str
    spotify_client_id: str
    spotify_client_secret: str

    def __init__(self, **settings):
        hints = typing.get_type_hints(type(self))
        for key, _type in hints.items():
            try:
                value = get_env_value(key)
            except KeyError:
                pass
            else:
                setattr(self, key, value)
                continue

            if key in settings:
                setattr(self, key, settings[key])

            if not hasattr(self, key):
                raise KeyError(f"Setting \"{key}\" needs to be set to {_type}!")

    @property
    def run_configuration(self) -> dict:
        return dict(host=self.HOST, port=self.PORT, workers=self.WORKER_AMOUNT)
