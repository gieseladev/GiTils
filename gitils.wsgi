#!/usr/bin/python
"""Apache start."""

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/GiTils/")

application = None


def run():
    """Run the server."""
    global application

    from GiTils import app

    application = app


run()
