import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Optional

import lyricsfinder
from motor.motor_asyncio import AsyncIOMotorDatabase
from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse

from gitils import Config, utils, GiTilsError

log = logging.getLogger(__name__)

blueprint = Blueprint()
executor = ProcessPoolExecutor()


class LyricsNotFound(GiTilsError):
    CODE = 404


async def find_lyrics(query: str, google_api_key: str) -> Optional[lyricsfinder.Lyrics]:
    searcher = lyricsfinder.search_lyrics(query, google_api_key=google_api_key)
    return await asyncio.get_event_loop().run_in_executor(executor, partial(next, searcher, None))


@blueprint.route("/lyrics/<query>")
async def get_lyrics(query: str, config: Config, mongo_db: AsyncIOMotorDatabase) -> JsonResponse:
    lyrics_data = await mongo_db.lyrics.find_one({"query": query})

    if not lyrics_data:
        lyrics = await find_lyrics(query, config.google_api_key)
        if not lyrics:
            raise LyricsNotFound(f"Couldn't find any lyrics for that query. ({query})")

        lyrics = lyrics.to_dict()
        lyrics_data = dict(lyrics=lyrics, query=query)
        await mongo_db.lyrics.insert_one(lyrics_data)
        log.debug(f"saved lyrics for query {query}")
    else:
        lyrics = lyrics_data["lyrics"]

    return utils.response(lyrics=lyrics)
