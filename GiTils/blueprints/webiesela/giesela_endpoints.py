from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse
from vibora import Request
from datetime import datetime
from gitils import utils

blueprint = Blueprint()

@blueprint.route("/giesela/register", methods=["post"])
async def register_giesela_instance(request:Request) -> JsonResponse:
    return utils.response(gitoken=None)


@blueprint.route("/giesela/login/<gitoken>", methods=["post"])
async def server_login(gitoken) -> JsonResponse:
    coll = mongo_database.giesela_servers
    ws_ip = request.remote_addr

    if gitoken == "new":
        res = coll.find_one({"ip": ws_ip})
        if res:
            gitoken = res["_id"]
        else:
            gitoken = ObjectId()
            res = {
                "secure": False,
                "port": 8000
            }
    else:
        try:
            gitoken = ObjectId(gitoken)
        except InvalidId:
            return error_response(Error.INVALID_REQUEST, f"The provided gitoken isn't a valid token ({gitoken})")

        res = coll.find_one({"_id": gitoken})
        if not res:
            return error_response(Error.TOKEN_UNKNOWN, f"This token isn't registered. ({gitoken})")

    ws_secure = cast_type(lambda v: v.lower() in {"true", "yes", "y", "t"}, request.args.get("secure"), res["secure"])
    ws_port = cast_type(int, request.args.get("port"), res["port"])

    ws_prefix = "wss" if ws_secure else "ws"
    ws_address = f"{ws_prefix}://{ws_ip}:{ws_port}"
    if not test_websocket(ws_address, current_app.config["WEBIESELA_WS_TIMEOUT"]):
        return error_response(Error.VALIDATION_ERROR, f"Couldn't validate address ({ws_address})")

    coll.update_one({"_id": gitoken}, {
        "$setOnInsert": {
            "tokens": [],
            "registered_at": datetime.utcnow()
        },
        "$set": {
            "address": ws_address,
            "ip": ws_ip,
            "port": ws_port,
            "secure": ws_secure,
            "last_edit_at": datetime.utcnow()
        }
    }, upsert=True)
    return response(address=ws_address, gitoken=str(gitoken))


@blueprint.route("/giesela/regtoken/<regtoken>", methods=["post"])
async def claim_token(regtoken) -> JsonResponse:
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

@blueprint.route("/giesela/token/<token>")
async def get_token_information(token) -> JsonResponse:
    pass