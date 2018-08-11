import base64
import time
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase
from vibora import Session
from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse

from gitils import Config, utils

blueprint = Blueprint()

SPOTIFY_AUTH_ENDPOINT = "https://accounts.spotify.com/api/token"


def get_spotify_auth_token(client_id: str, client_secret: str) -> str:
    return base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")


async def get_spotify_creds(session: Session, config: Config) -> Dict[str, Any]:
    token = get_spotify_auth_token(config.spotify_client_id, config.spotify_client_secret)
    headers = {"authorization": f"Basic {token}", "content-type": "application/x-www-form-urlencoded"}
    body = "grant_type=client_credentials".encode("utf-8")
    resp = await session.post(SPOTIFY_AUTH_ENDPOINT, headers=headers, body=body)
    _creds = resp.json()

    return {
        "access_token": _creds["access_token"],
        "expires_at": int(_creds["expires_in"] + time.time())
    }


@blueprint.route("/tokens/spotify")
async def get_spotify_token(config: Config, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    api_token_coll = mongo_db.api_tokens

    document = await api_token_coll.find_one("spotify")

    # Token should be valid for at least another minute otherwise it's kinda pointless...
    if not document or document["token"]["expires_at"] >= time.time() - 60:
        async with Session() as session:
            creds = await get_spotify_creds(session, config)
        await api_token_coll.insert_one(dict(_id="spotify", token=creds))
    else:
        creds = document["token"]

    return utils.response(**creds)
