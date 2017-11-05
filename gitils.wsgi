#!/usr/bin/python
import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/GiTils/")

application


def run():
    global application

    from GiTils import app

    application = app


run()
