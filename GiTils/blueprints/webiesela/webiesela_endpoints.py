import logging
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from vibora import Events, Request
from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse

from gitils import Config, InvalidRequest, utils
from .errors import TokenError
from .models import *
from .utils import generate_regtoken

log = logging.getLogger(__name__)

blueprint = Blueprint()

DB_INDEXES = {
    "regtokens": [dict(name="unique regtoken", unique=True, keys="regtoken"),
                  dict(name="deleting obsolete regtokens", keys="updated_at", expireAfterSeconds=3600)]
}


@blueprint.handle(Events.BEFORE_SERVER_START)
async def setup_database(mongo_db: AsyncIOMotorDatabase):
    await utils.create_indexes(mongo_db, DB_INDEXES)


@blueprint.route("/webiesela/endpoint/<webtoken>")
async def get_endpoint(webtoken: str, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    token = await Webtoken.aggregate(mongo_db, webtoken, giesela_instance=GieselaInstance)

    if not token:
        raise TokenError(f"Token doesn't exist! ({webtoken})", code=1)

    if not token.giesela_instance:
        raise InvalidRequest(f"Couldn't find Giesela endpoint for webtoken ({webtoken})")

    return utils.response(endpoint=token.giesela_instance.ws_url)


@blueprint.route("/webiesela/register")
async def register_user(request: Request, mongo_db: AsyncIOMotorDatabase, config: Config) -> JsonResponse:
    regtoken_coll = mongo_db.regtokens

    ip = request.client_ip()
    document = await regtoken_coll.find_one({"ip": ip})
    if not document:
        while True:
            regtoken = generate_regtoken(config.WEBIESELA_REGTOKEN_LENGTH)
            document = {
                "ip": ip,
                "regtoken": regtoken,
                "updated_at": datetime.utcnow()
            }
            try:
                await regtoken_coll.insert_one(document)
            except DuplicateKeyError:
                log.debug(f"Regtoken {regtoken} already in use, trying again")
                continue
            else:
                break

    return utils.response(webtoken=str(document["_id"]), regtoken=document["regtoken"])


@blueprint.route("/webiesela/check/<webtoken>")
async def check_registration(webtoken: str, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    try:
        webtoken = ObjectId(webtoken)
    except InvalidId:
        raise InvalidRequest(f"The provided webtoken isn't a valid webtoken ({webtoken})")

    regtoken = await Regtoken.find(mongo_db, webtoken)
    if not regtoken:
        raise TokenError(f"Couldn't find token, might have expired or doesn't exist ({webtoken})!", code=1)

    return utils.response(claimed=regtoken.claimed, endpoint=regtoken.endpoint)
