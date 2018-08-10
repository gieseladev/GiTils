__package__ = "gitils"

import logging.config
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

import raven
from raven.handlers.logging import SentryHandler

sys.path.append(str(Path(__file__).parent.parent))


def run(args: Namespace):
    import gitils
    gitils.run(host=args.host, port=args.port)


def main(*args):
    parser = ArgumentParser("gitils")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("-p", "--port", default=80)

    args = parser.parse_args(args or None)
    run(args)


def setup_logging():
    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "brief": {
                "format": "[{module}] {levelname}: {message}",
                "style": "{"
            },
            "detailed": {
                "format": "[{asctime}] {levelname} in {module}: {message}",
                "style": "{"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "level": "DEBUG",
                "filename": "gitils.log"
            }
        },
        "loggers": {
            "gitils": {
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console", "file"]
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    })

    from gitils import __version__

    sentry_client = raven.Client(release=__version__)
    sentry_handler = SentryHandler(sentry_client)
    sentry_handler.setLevel(logging.ERROR)
    logging.root.addHandler(sentry_handler)
    logging.getLogger("gitils").addHandler(sentry_handler)


if __name__ == "__main__":
    setup_logging()
    main()
