import json
import os

from . import utils


class Static:
    ROOT = None


class ConfigConst(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        try:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.split(script_path)[0]
            Static.ROOT = os.path.join(script_dir, os.pardir)
            rel_path = "config.json"
            abs_file_path = os.path.join(Static.ROOT, rel_path)

            with open(abs_file_path, "r") as f:
                data = json.load(f)

        except FileNotFoundError:
            raise FileNotFoundError("No config file found! Please create a config.json file at " + abs_file_path) from None
        except json.JSONDecodeError:
            raise Exception("Can't parse config file, please make sure it's valid JSON") from None

        for var, val in vars(cls).items():
            if var.isupper():
                setting_directions = utils.unravel_id(val or "{}.{}".format(name, var).lower())

                try:
                    setting_value = utils.traverse(data, setting_directions)
                except KeyError as e:
                    raise KeyError("Key \"{}\" missing in the config!".format(".".join(setting_directions))) from e

                setattr(cls, var, setting_value)


class Variables(metaclass=ConfigConst):
    GIESELA_IP = ""


class Spotify(metaclass=ConfigConst):
    CLIENT_ID = ""
    CLIENT_SECRET = ""


class Google(metaclass=ConfigConst):
    API_KEY = ""


class FileLocations:
    LYRICS = "data/lyrics"
