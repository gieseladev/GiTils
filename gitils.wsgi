#!/usr/bin/python
import logging
import sys

from GiTils import constants

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/GiTils/")


def run():
    from GiTils.gitils import app as application


run()
