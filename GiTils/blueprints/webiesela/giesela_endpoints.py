import asyncio
import logging
from datetime import datetime
from typing import Optional, Union
from urllib.parse import urlparse

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from vibora import Events, Request
from vibora.blueprints import Blueprint
from vibora.client.websocket import WebsocketClient
from vibora.responses import JsonResponse

from gitils import Config, utils
from gitils.errors import InvalidRequest
from .errors import TestConnectionError, TokenError
from .models import *
from .utils import is_valid_sha256

log = logging.getLogger(__name__)

blueprint = Blueprint()

DB_INDEXES = {
    "giesela_instances": [dict(name="unique gitoken", unique=True, keys="gitoken"),
                          dict(name="unique ws_url", unique=True, keys="ws_url")],
    # TODO do we really want them to be unique?
    # Maybe use a "last_used" parameter to delete them automatically after a few months
    "webiesela_tokens": dict(name="unique user+giesela_instance", unique=True, keys=[("user", pymongo.ASCENDING),
                                                                                     ("guild", pymongo.ASCENDING)])
}


@blueprint.handle(Events.BEFORE_SERVER_START)
async def setup_database(mongo_db: AsyncIOMotorDatabase):
    await utils.create_indexes(mongo_db, DB_INDEXES)


async def get_giesela_instance(gitoken: Optional[Union[str, dict, ObjectId]], mongo_db: AsyncIOMotorDatabase) -> GieselaInstance:
    if isinstance(gitoken, dict):
        gitoken = gitoken.get("gitoken")
    elif isinstance(gitoken, bytes):
        gitoken = gitoken.decode("utf-8")

    if isinstance(gitoken, str):
        try:
            gitoken = ObjectId(gitoken)
        except InvalidId:
            raise InvalidRequest(f"The provided gitoken isn't a valid gitoken ({gitoken})")

    if not gitoken:
        raise InvalidRequest("No \"gitoken\" provided")

    instance = await GieselaInstance.find(mongo_db, dict(gitoken=gitoken))
    if not instance:
        raise TokenError(f"Gitoken is invalid! ({gitoken})", code=1)
    return instance


async def test_giesela_websocket(url: str, hashed_code: str, timeout: float) -> None:
    if not is_valid_sha256(hashed_code):
        raise InvalidRequest(f"Provided Hash isn't a valid hash code! ({hashed_code})")

    parsed = urlparse(url)
    client = WebsocketClient(parsed.hostname, parsed.port, "/gitils")

    try:
        await asyncio.wait_for(client.connect(), timeout)
    except asyncio.TimeoutError:
        raise TestConnectionError("Connection timed out", code=1)
    else:
        # TODO get information and close connection
        return


@blueprint.route("/giesela/register", methods=["post"])
async def register_giesela_instance(request: Request, mongo_db: AsyncIOMotorDatabase, config: Config) -> JsonResponse:
    data = await request.json()

    ws_url = data.get("ws_url")
    if not ws_url:
        raise InvalidRequest("No \"ws_url\" provided")

    hashed_code = data.get("hash")
    # TODO store this hash and reuse it when logging in?

    await test_giesela_websocket(ws_url, hashed_code, config.WEBIESELA_WEBSOCKET_TIMEOUT)
    giesela_instance = await GieselaInstance.create(mongo_db, ws_url=ws_url, last_login_at=datetime.utcnow())

    return utils.response(gitoken=giesela_instance.gitoken)


@blueprint.route("/giesela/login/<gitoken>", methods=["post"])
async def giesela_instance_login(gitoken: str, request: Request, mongo_db: AsyncIOMotorDatabase, config: Config) -> JsonResponse:
    data = await request.json()
    giesela_instance = await get_giesela_instance(gitoken, mongo_db)

    ws_url = giesela_instance.ws_url
    hashed_code = data.get("hash")

    await test_giesela_websocket(ws_url, hashed_code, config.WEBIESELA_WEBSOCKET_TIMEOUT)

    await giesela_instance.set(last_login_at=datetime.utcnow())

    return utils.response()


@blueprint.route("/giesela/claim/<regtoken>", methods=["post"])
async def claim_regtoken(regtoken: str, request: Request, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    data = await request.json()
    user_id = data.get("user_id")  # TODO create user if it doesn't exist

    giesela_instance = await get_giesela_instance(data, mongo_db)

    token = await Regtoken.find(mongo_db, regtoken)

    if not token:
        raise TokenError(f"This token may have expired or is invalid ({regtoken})", code=1)

    if token.claimed:
        raise TokenError(f"This token has already been claimed ({regtoken})", code=4)

    await token.set(claimed=True, endpoint=giesela_instance.ws_url, updated_at=datetime.utcnow())
    await Webtoken.create(mongo_db, _id=token.webtoken, user=user_id, giesela_instance=giesela_instance.gid)
    return utils.response()


@blueprint.route("/giesela/webtoken/<webtoken>")
async def get_webtoken_information(webtoken: str, request: Request, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    giesela_instance = await get_giesela_instance(request.args.get(b"gitoken"), mongo_db)

    webtoken = utils.cast_as(request.args.get(b"webtoken").decode("utf-8"), ObjectId, TokenError(f"Webtoken is invalid! ({webtoken})", code=1))

    token = await Webtoken.aggregate(mongo_db, webtoken, giesela_instance=GieselaInstance, user=User)

    if not token:
        raise TokenError(f"Token doesn't exist! ({webtoken})", code=1)

    if not token.giesela_instance:
        raise InvalidRequest(f"Couldn't find Giesela endpoint for webtoken ({webtoken})")

    if giesela_instance.gid != token.giesela_instance.gid:
        raise TokenError(f"Token doesn't belong to this instance!", 4)

    user: User = token.user
    return utils.response(user_id=user.user_id)
