#!/usr/bin/python
import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/GiTils/")


def run():
    from GiTils import app as application


run()
