import logging
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, PyMongoError
from vibora import Events, Request
from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse

from gitils import Config, InvalidRequest, utils
from .errors import TokenError
from .utils import generate_regtoken

log = logging.getLogger(__name__)

blueprint = Blueprint()

DB_INDEXES = [
    ("registration_tokens", dict(name="unique regtoken", unique=True, keys="regtoken")),
    ("registration_tokens", dict(name="deleting obsolete regtokens", keys="updated_at", expireAfterSeconds=3600))
]


@blueprint.handle(Events.BEFORE_SERVER_START)
async def setup_database(mongo_db: AsyncIOMotorDatabase):
    for collection, kwargs in DB_INDEXES:
        try:
            await mongo_db[collection].create_index(**kwargs)
        except PyMongoError:
            log.exception(f"Couldn't create index for collection {collection}")


@blueprint.route("/webiesela/endpoint/<token>")
async def get_endpoint(token: str, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    try:
        token = ObjectId(token)
    except InvalidId:
        raise InvalidRequest(f"The provided token isn't a valid token ({token})")

    document = await mongo_db.webiesela_tokens.find_one(token)

    if not document:
        raise TokenError(f"token isn't bound to any Giesela instance ({token})", code=1)

    document = await mongo_db.giesela_instances.find_one(document["gid"])

    return utils.response(endpoint=document["address"])


@blueprint.route("/webiesela/register")
async def register_user(request: Request, mongo_db: AsyncIOMotorDatabase, config: Config) -> JsonResponse:
    coll = mongo_db.registration_tokens

    ip = request.client_ip()
    document = await coll.find_one({"ip": ip})
    if not document:
        while True:
            document = {
                "ip": ip,
                "regtoken": generate_regtoken(config.WEBIESELA_REGTOKEN_LENGTH),
                "updated_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            try:
                await coll.insert_one(document)
            except DuplicateKeyError:
                continue
            else:
                break

    return utils.response(token=str(document["_id"]), regtoken=document["regtoken"])


@blueprint.route("/webiesela/check/<token>")
async def check_registration(token: str, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    coll = mongo_db.registration_tokens

    try:
        token = ObjectId(token)
    except InvalidId:
        raise InvalidRequest(f"The provided token isn't a valid token ({token})")

    res = await coll.find_one(token)
    if not res:
        raise TokenError(f"Couldn't find token, might have expired or doesn't exist ({token})!", code=2)

    # TODO: Check the status of the token
    return utils.response(claimed=res.get("claimed", False), endpoint=res.get("endpoint"))
