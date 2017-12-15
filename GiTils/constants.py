"""Constants."""
import json
import os

from . import utils


class Static:
    """Static things."""

    ROOT = None


class ConfigConst(type):
    """When using this class as a metaclass it will load the string from the settings."""

    data = None

    def __init__(cls, name, bases, attrs, **kwargs):
        """Load the settings from file."""
        if not ConfigConst.data:
            try:
                script_path = os.path.abspath(__file__)
                script_dir = os.path.split(script_path)[0]
                Static.ROOT = os.path.join(script_dir, os.pardir)
                rel_path = "config.json"
                abs_file_path = os.path.join(Static.ROOT, rel_path)

                with open(abs_file_path, "r") as f:
                    ConfigConst.data = json.load(f)

            except FileNotFoundError:
                raise FileNotFoundError("No config file found! Please create a config.json file at " + abs_file_path) from None
            except json.JSONDecodeError:
                raise Exception("Can't parse config file, please make sure it's valid JSON") from None

        data = ConfigConst.data

        for var, val in vars(cls).items():
            if var.isupper():
                setting_directions = utils.unravel_id(val or "{}.{}".format(name, var).lower())

                try:
                    setting_value = utils.traverse(data, setting_directions)
                except KeyError as e:
                    raise KeyError("Key \"{}\" missing in the config!".format(".".join(setting_directions))) from e

                setattr(cls, var, setting_value)


class Variables(metaclass=ConfigConst):
    """Various misc settings."""

    GIESELA_IP = ""


class Spotify(metaclass=ConfigConst):
    """Settings for Spotify token."""

    CLIENT_ID = ""
    CLIENT_SECRET = ""


class Google(metaclass=ConfigConst):
    """Google api stuff."""

    API_KEY = ""


class FileLocations:
    """Various file/folder locations."""

    LYRICS = "data/lyrics"
