#!/usr/bin/python
"""Flask, uWSGI served on nginx"""

import logging
import sys

from GiTils import app

logging.basicConfig(stream=sys.stderr)

application = app

if __name__ == '__main__': application.run(host='0.0.0.0')
