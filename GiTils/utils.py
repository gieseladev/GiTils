from typing import Any, Callable, TypeVar

from vibora.responses import JsonResponse

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


def cast_type(cls: Callable[[TV], T], val: Any, default: Any = _DEFAULT) -> T:
    try:
        return cls(val)
    except Exception as e:
        if default is _DEFAULT:
            raise e
        return default
