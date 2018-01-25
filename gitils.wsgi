#!/usr/bin/python
"""Apache start."""

import logging
import sys

from GiTils import app

logging.basicConfig(stream=sys.stderr)

application = app
application.run()
