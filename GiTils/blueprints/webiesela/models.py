from functools import wraps
from typing import Awaitable, Callable, Optional, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

RT = TypeVar("RT")
IT = TypeVar("IT")


def cached_property(func: Callable[[IT], Awaitable[RT]]) -> property:
    cache_key = func.__name__

    @wraps(func)
    async def wrapper(self: IT) -> RT:
        if cache_key not in self._cache:
            self.__cache__[cache_key] = await func(self)
        return self.__cache__[cache_key]

    return property(wrapper)


class GieselaInstance:
    mongo_db: AsyncIOMotorDatabase
    gid: ObjectId

    def __init__(self, mongo_db: AsyncIOMotorDatabase, gid: ObjectId):
        self.mongo_db = mongo_db
        self.gid = gid

        self.__cache__ = {}

    @cached_property
    async def instance_information(self) -> Optional[dict]:
        return await self.mongo_db.giesela_instances.find_one(self.gid)

    @property
    async def exists(self) -> bool:
        return bool(await self.instance_information)

    @property
    async def host(self) -> str:
        instance_information = await self.instance_information
        return instance_information["host"]

    @property
    async def port(self) -> int:
        instance_information = await self.instance_information
        return instance_information["port"]

    @property
    async def address(self) -> str:
        pass

    def clear(self):
        self.__cache__.clear()
