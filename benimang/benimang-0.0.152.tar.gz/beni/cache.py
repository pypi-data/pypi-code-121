import inspect
from functools import wraps
from typing import Any, NamedTuple, cast

import beni


class _CachedResult(NamedTuple):
    par: Any
    result: Any


_cachedFuncResult: dict[str, dict[Any, list[_CachedResult]]] = {}


def cache(*groupNameList: str):
    groupNameList = groupNameList or ('',)

    def wraperfun(func: beni.AsyncFun) -> beni.AsyncFun:
        @wraps(func)
        async def wraper(*args: Any, **kwargs: Any):
            target_func = inspect.unwrap(func)
            par = [args, kwargs]
            cached_list: list[_CachedResult] = []
            for groupname in groupNameList:
                if groupname not in _cachedFuncResult:
                    _cachedFuncResult[groupname] = {}
                if target_func not in _cachedFuncResult[groupname]:
                    _cachedFuncResult[groupname][target_func] = cached_list
                else:
                    cached_list = _cachedFuncResult[groupname][target_func]
            for cached_result in cached_list:
                if cached_result.par == par:
                    return cached_result.result
            result = await func(*args, **kwargs)
            cached_list.append(_CachedResult(par, result))
            return result
        return cast(Any, wraper)
    return wraperfun


def clear(*groupNameList: str):
    groupNameList = groupNameList or ('',)
    clearCache(*groupNameList)

    def wraperfun(func: beni.AsyncFun) -> beni.AsyncFun:
        @wraps(func)
        async def wraper(*args: Any, **kwargs: Any):
            return await func(*args, **kwargs)
        return cast(Any, wraper)
    return wraperfun


def clearCache(*funcOrGroupNameList: Any):
    for func_or_groupname in funcOrGroupNameList:
        if type(func_or_groupname) is str:
            groupname = func_or_groupname
            if groupname in _cachedFuncResult:
                for cached_list in _cachedFuncResult[groupname].values():
                    cached_list.clear()
        else:
            func = inspect.unwrap(func_or_groupname)
            for data in _cachedFuncResult.values():
                for k in data.keys():
                    if k == func:
                        data[k].clear()
