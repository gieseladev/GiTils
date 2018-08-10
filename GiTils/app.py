import importlib

from vibora import Events, Response, Vibora
from vibora.responses import JsonResponse

from . import __info__, components, utils
from .config import Config
from .errors import GiTilsError

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


for bp in config.active_blueprints:
    module = importlib.import_module(f"{__package__}.blueprints.{bp}")
    app.add_blueprint(module.blueprint)


def run(**options):
    kwargs = config.run_configuration.copy()
    kwargs.update(options)
    app.run(**kwargs)
