import importlib
import logging
from typing import Iterable

from vibora import Events, Response, Vibora
from vibora.responses import JsonResponse

from . import __info__, components, utils
from .config import Config
from .errors import GiTilsError

log = logging.getLogger(__name__)

config = Config()
app = Vibora()


@app.handle(Events.BEFORE_SERVER_START)
async def before_server_start():
    components.add_components(app, config)


@app.handle(Events.AFTER_ENDPOINT)
async def before_response(response: Response):
    response.headers["gitils-version"] = __info__.__version__


@app.handle(GiTilsError)
async def handle_error(error: GiTilsError) -> JsonResponse:
    return utils.error_response(error)


for name in config.active_blueprints:
    module = importlib.import_module(f"{__package__}.blueprints.{name}")
    _blueprint = module.blueprint
    if isinstance(_blueprint, Iterable):
        for blueprint in _blueprint:
            app.add_blueprint(blueprint)
    else:
        app.add_blueprint(_blueprint)


def run(**options):
    kwargs = config.run_configuration.copy()
    kwargs.update(options)
    log.info("starting server")
    app.run(**kwargs)
