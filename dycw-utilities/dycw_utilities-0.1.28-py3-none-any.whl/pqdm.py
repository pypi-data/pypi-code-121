from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from functools import partial
from io import StringIO
from io import TextIOWrapper
from multiprocessing import cpu_count
from typing import Any
from typing import Literal
from typing import Optional
from typing import TypeVar
from typing import Union
from typing import cast

from pqdm import processes

from dycw_utilities.tqdm import tqdm


_T = TypeVar("_T")


def pmap(
    func: Callable[..., _T],
    /,
    *iterables: Iterable[Any],
    parallelism: Literal["processes", "threads"] = "processes",
    n_jobs: Optional[int] = None,
    bounded: bool = False,
    exception_behaviour: Literal["ignore", "immediate", "deferred"] = "ignore",
    desc: Optional[str] = None,
    total: Optional[Union[int, float]] = None,
    leave: Optional[bool] = True,
    file: Optional[Union[TextIOWrapper, StringIO]] = None,
    ncols: Optional[int] = None,
    mininterval: Optional[float] = 0.1,
    maxinterval: Optional[float] = 10,
    miniters: Optional[Union[int, float]] = None,
    ascii: Optional[Union[bool, str]] = None,
    unit: Optional[str] = "it",
    unit_scale: Optional[Union[bool, int, str]] = False,
    dynamic_ncols: Optional[bool] = False,
    smoothing: Optional[float] = 0.3,
    bar_format: Optional[str] = None,
    initial: Optional[Union[int, float]] = 0,
    position: Optional[int] = None,
    postfix: Optional[Mapping[str, Any]] = None,
    unit_divisor: Optional[float] = 1000,
    write_bytes: Optional[bool] = None,
    lock_args: Optional[tuple[Any, ...]] = None,
    nrows: Optional[int] = None,
    colour: Optional[str] = None,
    delay: Optional[float] = 0,
    gui: Optional[bool] = False,
    **kwargs: Any,
) -> list[_T]:
    """Parallel map, powered by `pqdm`."""

    return pstarmap(
        func,
        zip(*iterables),
        parallelism=parallelism,
        n_jobs=n_jobs,
        bounded=bounded,
        exception_behaviour=exception_behaviour,
        desc=desc,
        total=total,
        leave=leave,
        file=file,
        ncols=ncols,
        mininterval=mininterval,
        maxinterval=maxinterval,
        miniters=miniters,
        ascii=ascii,
        unit=unit,
        unit_scale=unit_scale,
        dynamic_ncols=dynamic_ncols,
        smoothing=smoothing,
        bar_format=bar_format,
        initial=initial,
        position=position,
        postfix=postfix,
        unit_divisor=unit_divisor,
        write_bytes=write_bytes,
        lock_args=lock_args,
        nrows=nrows,
        colour=colour,
        delay=delay,
        gui=gui,
        **kwargs,
    )


def pstarmap(
    func: Callable[..., _T],
    iterable: Iterable[tuple[Any, ...]],
    /,
    *,
    parallelism: Literal["processes", "threads"] = "processes",
    n_jobs: Optional[int] = None,
    bounded: bool = False,
    exception_behaviour: Literal["ignore", "immediate", "deferred"] = "ignore",
    desc: Optional[str] = None,
    total: Optional[Union[int, float]] = None,
    leave: Optional[bool] = True,
    file: Optional[Union[TextIOWrapper, StringIO]] = None,
    ncols: Optional[int] = None,
    mininterval: Optional[float] = 0.1,
    maxinterval: Optional[float] = 10,
    miniters: Optional[Union[int, float]] = None,
    ascii: Optional[Union[bool, str]] = None,
    unit: Optional[str] = "it",
    unit_scale: Optional[Union[bool, int, str]] = False,
    dynamic_ncols: Optional[bool] = False,
    smoothing: Optional[float] = 0.3,
    bar_format: Optional[str] = None,
    initial: Optional[Union[int, float]] = 0,
    position: Optional[int] = None,
    postfix: Optional[Mapping[str, Any]] = None,
    unit_divisor: Optional[float] = 1000,
    write_bytes: Optional[bool] = None,
    lock_args: Optional[tuple[Any, ...]] = None,
    nrows: Optional[int] = None,
    colour: Optional[str] = None,
    delay: Optional[float] = 0,
    gui: Optional[bool] = False,
    **kwargs: Any,
) -> list[_T]:
    """Parallel map, powered by `pqdm`."""

    n_jobs = _get_n_jobs(n_jobs)
    tqdm_class = cast(Any, tqdm)
    if parallelism == "processes":
        result = processes.pqdm(
            iterable,
            partial(_starmap_helper, func),
            n_jobs=n_jobs,
            argument_type="args",
            bounded=bounded,
            exception_behaviour=exception_behaviour,
            tqdm_class=tqdm_class,
            **({} if desc is None else {"desc": desc}),
            total=total,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=mininterval,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            unit=unit,
            unit_scale=unit_scale,
            dynamic_ncols=dynamic_ncols,
            smoothing=smoothing,
            bar_format=bar_format,
            initial=initial,
            position=position,
            postfix=postfix,
            unit_divisor=unit_divisor,
            write_bytes=write_bytes,
            lock_args=lock_args,
            nrows=nrows,
            colour=colour,
            delay=delay,
            gui=gui,
            **kwargs,
        )
    else:
        result = processes.pqdm(
            iterable,
            partial(_starmap_helper, func),
            n_jobs=n_jobs,
            argument_type="args",
            bounded=bounded,
            exception_behaviour=exception_behaviour,
            tqdm_class=tqdm_class,
            **({} if desc is None else {"desc": desc}),
            total=total,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=mininterval,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            unit=unit,
            unit_scale=unit_scale,
            dynamic_ncols=dynamic_ncols,
            smoothing=smoothing,
            bar_format=bar_format,
            initial=initial,
            position=position,
            postfix=postfix,
            unit_divisor=unit_divisor,
            write_bytes=write_bytes,
            lock_args=lock_args,
            nrows=nrows,
            colour=colour,
            delay=delay,
            gui=gui,
            **kwargs,
        )
    return list(result)


def _get_n_jobs(n_jobs: Optional[int], /) -> int:
    if (n_jobs is None) or (n_jobs <= 0):
        return cpu_count()  # pragma: no cover
    else:
        return n_jobs


def _starmap_helper(func: Callable[..., _T], *args: Any) -> _T:
    return func(*args)
