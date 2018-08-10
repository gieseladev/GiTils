import logging
from datetime import datetime
from urllib.parse import urlparse

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from vibora import Events, Request
from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse

from gitils import Config, InvalidRequest, utils
from .errors import LoginError, TokenError
from .utils import test_giesela_websocket

log = logging.getLogger(__name__)

blueprint = Blueprint()

DB_INDEXES = [
    ("giesela_instances", dict(name="unique gitoken", unique=True, keys="gitoken")),
    ("giesela_instances", dict(name="unique ws_url", unique=True, keys="ws_url"))
]


@blueprint.handle(Events.BEFORE_SERVER_START)
async def setup_database(mongo_db: AsyncIOMotorDatabase):
    for collection, kwargs in DB_INDEXES:
        try:
            await mongo_db[collection].create_index(**kwargs)
        except PyMongoError:
            log.exception(f"Couldn't create index for collection {collection}")


@blueprint.route("/giesela/register", methods=["post"])
async def register_giesela_instance(request: Request, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    coll = mongo_db.giesela_instances
    return utils.response(gitoken=None)


@blueprint.route("/giesela/login/<gitoken>", methods=["post"])
async def giesela_instance_login(gitoken: str, request: Request, mongo_db: AsyncIOMotorDatabase, config: Config) -> JsonResponse:
    coll = mongo_db.giesela_instances

    try:
        gitoken = ObjectId(gitoken)
    except InvalidId:
        raise InvalidRequest(f"The provided gitoken isn't a valid token ({gitoken})")

    res = await coll.find_one({"gitoken": gitoken})
    if not res:
        raise TokenError(f"This token isn't registered. ({gitoken})", code=3)

    ws_url = res["ws_url"]
    parsed = urlparse(ws_url)

    result = await test_giesela_websocket(parsed.hostname, parsed.port, config.WEBIESELA_WEBSOCKET_TIMEOUT)
    if not result:
        raise LoginError(f"Couldn't validate address ({ws_url})", code=1)

    await coll.update_one({"gitoken": gitoken}, {
        "$currentData": {
            "last_login_at": True
        }
    })

    return utils.response()


@blueprint.route("/giesela/register/<regtoken>", methods=["post"])
async def claim_regtoken(regtoken: str, request: Request, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    gitoken = request  # TODO extract token from arguments

    instance_coll = mongo_db.giesela_instances
    giesela_instance = await instance_coll.find_one({"gitoken": gitoken})
    if not giesela_instance:
        raise TokenError(f"No Giesela instance with gitoken! ({gitoken})")

    token_coll = mongo_db.registration_tokens
    token = await token_coll.find_one({"regtoken": regtoken})

    if not token:
        raise TokenError(f"This token may have expired or is invalid ({regtoken})", code=2)
    elif token.get("claimed", False):
        raise TokenError(f"This token has already been claimed ({regtoken})", code=4)

    await token_coll.update_one({"regtoken": regtoken}, {
        "$set": {
            "claimed": True,
            "endpoint": giesela_instance["ws_url"],
            "updated_at": datetime.utcnow()
        }
    })
    return utils.response(token=token["_id"])


@blueprint.route("/giesela/token/<token>")
async def get_token_information(token) -> JsonResponse:
    pass
