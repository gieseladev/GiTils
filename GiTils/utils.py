import logging
from typing import Any, Callable, Dict, List, TypeVar, Union

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from vibora.responses import JsonResponse

log = logging.getLogger(__name__)
_DEFAULT = object()


def response(*data: Any, success: bool = True, **kwargs) -> JsonResponse:
    kwargs["success"] = success

    data = list(data)
    if len(data) == 1:
        kwargs["data"] = data[0]
    elif len(data) > 0:
        kwargs["data"] = data

    return JsonResponse(kwargs)


def error_response(error: Exception) -> JsonResponse:
    error = {
        "name": getattr(error, "NAME", False) or type(error).__name__,
        "code": getattr(error, "CODE", 0),
        "msg": getattr(error, "msg", False) or str(error)
    }
    return response(error=error, success=False)


T = TypeVar("T")
TV = TypeVar("TV")


def cast_as(val: Any, cls: Callable[[TV], T], default: Any = _DEFAULT, *, raise_default: bool = True) -> T:
    try:
        return cls(val)
    except Exception as e:
        if default is _DEFAULT:
            raise e
        elif raise_default and isinstance(default, Exception):
            raise default
        return default


IndexType = Dict[str, Any]


async def create_indexes(mongo_db: AsyncIOMotorDatabase, index_map: Dict[str, Union[IndexType, List[IndexType]]]):
    for collection, indexes in index_map.items():
        indexes = indexes if isinstance(indexes, list) else [indexes]
        for index in indexes:
            try:
                await mongo_db[collection].create_index(**index)
            except PyMongoError:
                log.warning(f"Couldn't create index for collection {collection}")
