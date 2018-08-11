import typing
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

__all__ = ["GieselaInstance", "Regtoken", "User", "Webtoken"]


class DbObject:
    COLLECTION_NAME: str
    DEFAULT_SEARCH_NAME: str = "_id"
    EXCLUDED = ("COLLECTION_NAME", "DEFAULT_SEARCH_NAME", "EXCLUDED", "mongo_db", "mongo_coll", "_proxies")

    _id: Any
    mongo_db: AsyncIOMotorDatabase
    mongo_coll: AsyncIOMotorCollection

    _proxies: Dict[str, str]

    def __init__(self, mongo_db: AsyncIOMotorDatabase, data: dict):
        self.mongo_db = mongo_db
        self.mongo_coll = mongo_db[self.COLLECTION_NAME]

        self.EXCLUDED = set(attr for base in type(self).__mro__ for attr in getattr(base, "EXCLUDED", []))
        self._proxies = {}

        hints = typing.get_type_hints(type(self))
        for name, _type in hints.items():
            if name in self.EXCLUDED:
                continue
            if name in data:
                setattr(self, name, data[name])
            elif hasattr(self, name):
                value = getattr(self, name)
                if isinstance(value, str):
                    if value.startswith("$"):
                        real_name = value[1:]
                        value = data[real_name]
                        setattr(self, name, value)
                        setattr(self, real_name, value)
                        self._proxies[name] = real_name
            else:
                raise KeyError(f"Couldn't find \"{name}\" in object")

    def __repr__(self) -> str:
        _id = getattr(self, self.DEFAULT_SEARCH_NAME, "unknown id")
        return f"<{type(self).__name__} {_id}>"

    def __contains__(self, item: str) -> bool:
        return item in self.document

    def __getattr__(self, item: str) -> Any:
        print("hey there", self, item)

    def _proxy(self):
        raise AttributeError

    @property
    def document(self) -> dict:
        data = vars(self)
        return {key: value for key, value in data.items() if not (key in self.EXCLUDED or key in self._proxies)}

    @property
    def generation_time(self) -> Optional[datetime]:
        if isinstance(self._id, ObjectId):
            return self._id.generation_time

    @classmethod
    async def aggregate(cls, mongo_db: AsyncIOMotorDatabase, target: Any, **fields: Type["DbObject"]) -> Optional["DbObject"]:
        return await aggregate_single(mongo_db, cls, target, **fields)

    @classmethod
    async def find(cls, mongo_db: AsyncIOMotorDatabase, target: Any) -> Optional["DbObject"]:
        coll = mongo_db[cls.COLLECTION_NAME]
        target = cls.get_target_dict(target)

        document = await coll.find_one(target)
        if not document:
            return None
        return cls(mongo_db, document)

    @classmethod
    async def create(cls, mongo_db: AsyncIOMotorDatabase, **kwargs) -> "DbObject":
        kwargs.setdefault("_id", None)

        inst = cls(mongo_db, kwargs)
        document = inst.document

        if document["_id"] is None:
            del document["_id"]

        result = await inst.mongo_coll.insert_one(inst.document)
        inst._id = result.inserted_id
        return inst

    @classmethod
    def get_target_dict(cls, target: Any) -> dict:
        if not isinstance(target, dict):
            target = {cls.DEFAULT_SEARCH_NAME: target}
        return target

    async def set(self, **data):
        await self.mongo_coll.update_one(dict(_id=self._id), {"$set": data})
        for key, value in data.items():
            setattr(self, key, value)


DT = TypeVar("DT", bound=DbObject)


async def aggregate_single(mongo_db: AsyncIOMotorDatabase, cls: Type[DT], target: Any, **fields: Type["DbObject"]) -> Optional[DT]:
    coll = mongo_db[cls.COLLECTION_NAME]
    pipeline = []

    target = cls.get_target_dict(target)
    pipeline.append({"$match": target})

    for local_field, target in fields.items():
        pipeline.append({"$lookup": {
            "from": target.COLLECTION_NAME,
            "localField": local_field,
            "foreignField": "_id",
            "as": local_field
        }})

    cursor = coll.aggregate(pipeline)
    await cursor.fetch_next
    document = cursor.next_object()

    if not document:
        return None

    for field, target_cls in fields.items():
        value = next(iter(document[field]), None)
        if value:
            value = target_cls(mongo_db, value)
        document[field] = value

    db_obj = cls(mongo_db, document)
    return db_obj


class GieselaInstance(DbObject):
    COLLECTION_NAME = "giesela_instances"
    DEFAULT_SEARCH_NAME = "gitoken"

    gid: ObjectId = "$_id"
    ws_url: str
    gitoken: str
    last_login_at: datetime


class Regtoken(DbObject):
    COLLECTION_NAME = "regtokens"
    DEFAULT_SEARCH_NAME = "regtoken"

    webtoken: ObjectId = "$_id"
    regtoken: str
    ip: str
    claimed: bool = False
    endpoint: str = None
    updated_at: datetime


class User(DbObject):
    COLLECTION_NAME = "users"

    user_id: int = "$_id"


class Webtoken(DbObject):
    COLLECTION_NAME = "webtokens"

    webtoken: ObjectId = "$_id"
    user: int
    giesela_instance: ObjectId
