"""Webiesela manager.

Terminology:
    gitoken - "Giesela Instance Token" A token used to identify Giesela instances
    regtoken - "Registration Token" A short token generated to determine the identity of a web user.
"""

import logging
import random
from datetime import datetime
from enum import IntEnum
from string import ascii_uppercase
from threading import Lock, Thread

from bson.objectid import InvalidId, ObjectId
from flask import Blueprint, current_app, jsonify, request
from pymongo.errors import DuplicateKeyError

from GiTils.gitils import mongo_database
from websocket import WebSocketException, create_connection

log = logging.getLogger(__name__)

blueprint = Blueprint("Webiesela", __name__, url_prefix="/webiesela")

ws_test_lock = Lock()


class Error(IntEnum):
    """Error codes."""

    GENERAL = 0
    INVALID_REQUEST = 1

    VALIDATION_ERROR = 1001
    ALREADY_REGISTERED = 1002

    TOKEN_UNKNOWN = 2001
    TOKEN_CLAIMED = 2002

    SERVER_NOT_FOUND = 3001


def response(**kwargs):
    """Return a response."""
    data = kwargs
    data["success"] = kwargs.get("success", True)
    return jsonify(data)


def error_response(error, msg):
    """Return an error response."""
    error = {
        "name": error.name,
        "code": error.value,
        "msg": msg
    }
    return response(error=error, success=False)


def _test_websocket(addr):
    """Try to connect with addr and validate it."""
    try:
        ws = create_connection(addr)
    except Exception:
        test_websocket.result = False
        return

    try:
        # TODO: get some info
        pass
    except WebSocketException:
        test_websocket.result = False
    finally:
        ws.close()
    test_websocket.result = True


def test_websocket(addr, timeout):
    """Wraps around _test_websocket with a timeout."""
    # Using this lock just to be sure. Calling join right after start SHOULD in theory prevent unpredictable results from happening but juuuust to be sure.
    with ws_test_lock:
        test_websocket.result = False
        thread = Thread(target=_test_websocket, args=(addr,))
        thread.start()
        thread.join(timeout)
        return test_websocket.result


def generate_regtoken(length, population=ascii_uppercase):
    """Generate a token.

    This token is NOT guaranteed to be unique!
    """
    token = "".join(random.choices(population, k=length))
    return token


@blueprint.route("/server/login")
def server_login():
    """Register a Giesela instance."""
    ws_ip = request.remote_addr

    coll = mongo_database.giesela_servers
    res = coll.find_one({"ip": ws_ip})
    if res:
        default_secure = res["secure"]
        default_port = res["port"]
    else:
        default_secure = False
        default_port = 8000

    ws_secure = request.args.get("secure", default_secure)
    ws_port = request.args.get("port", default_port)

    ws_prefix = "wss" if ws_secure else "ws"
    ws_address = f"{ws_prefix}://{ws_ip}:{ws_port}"
    if not test_websocket(ws_address, current_app.config["WEBIESELA_WS_TIMEOUT"]):
        return error_response(Error.VALIDATION_ERROR, f"Couldn't validate address ({ws_address})")

    # THIS IS AWESOME!
    coll.update_one({"ip": ws_ip}, {
        "$setOnInsert": {
            "ip": ws_ip,
            "tokens": [],
            "registered_at": datetime.utcnow()
        },
        "$set": {
            "address": ws_address,
            "port": ws_port,
            "secure": ws_secure,
            "last_edit_at": datetime.utcnow()
        }
    }, upsert=True)
    return response(address=ws_address)


@blueprint.route("/endpoint/<token>")
def get_endpoint(token):
    """Get the appropriate address for a Giesela instance identified by the token."""
    try:
        token = ObjectId(token)
    except InvalidId:
        return error_response(Error.INVALID_REQUEST, f"The provided token isn't a valid token ({token})")
    coll = mongo_database.giesela_servers

    res = coll.find_one({"tokens": token})
    if not res:
        return error_response(Error.TOKEN_UNKNOWN, f"token isn't bound to any server ({token})")

    endpoint = {
        "address": res["address"],
        "secure": res["secure"],
        "ip": res["ip"],
        "port": res["port"]
    }
    return response(**endpoint)


@blueprint.route("/registration/register")
def register_user():
    """Start the registration progress for a user."""
    ip = request.remote_addr
    coll = mongo_database.registration_tokens
    document = coll.find_one({"ip": ip})
    if not document:
        while True:
            document = {
                "ip": ip,
                "regtoken": generate_regtoken(current_app.config["WEBIESELA_REGTOKEN_LENGTH"]),
                "claimed": False,
                "endpoint": None,
                "updated_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            try:
                coll.insert_one(document)
            except DuplicateKeyError:
                continue
            else:
                break

    return response(token=str(document["_id"]), regtoken=document["regtoken"])


@blueprint.route("/registration/check/<regtoken>")
def check_registration(regtoken):
    """Check whether regtoken has been registered."""
    coll = mongo_database.registration_tokens
    res = coll.find_one({"regtoken": regtoken})
    if res:
        # TODO: Check the status of the token
        return response(token=str(res["_id"]), claimed=res["claimed"], endpoint=res["endpoint"])
    else:
        return error_response(Error.TOKEN_UNKNOWN, f"This token may have expired or is invalid ({regtoken})")


@blueprint.route("/registration/claim/<regtoken>")
def claim_token(regtoken):
    """Giesela instance claim regtoken."""
    ip = request.remote_addr
    server_coll = mongo_database.giesela_servers
    server = server_coll.find_one({"ip": ip})
    if not server:
        return error_response(Error.SERVER_NOT_FOUND, f"No server with this ip address exists! ({ip})")
    token_coll = mongo_database.registration_tokens
    token = token_coll.find_one({"regtoken": regtoken})
    if not token:
        return error_response(Error.TOKEN_UNKNOWN, f"This token may have expired or is invalid ({regtoken})")
    elif token["claimed"]:
        return error_response(Error.TOKEN_CLAIMED, f"This token has already been claimed ({regtoken})")

    server_coll.update_one({"ip": ip}, {
        "$addToSet": {
            "tokens": token["_id"]
        }
    })

    endpoint = {
        "address": server["address"],
        "secure": server["secure"],
        "ip": server["ip"],
        "port": server["port"]
    }
    token_coll.update_one({"regtoken": regtoken}, {
        "$set": {
            "claimed": True,
            "endpoint": endpoint,
            "updated_at": datetime.utcnow()
        }
    })
    return response(token=token["_id"])
