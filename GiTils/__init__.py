import importlib

from .__info__ import *
from .config import Config
from .errors import *

run = importlib.import_module(".app", __package__).run
