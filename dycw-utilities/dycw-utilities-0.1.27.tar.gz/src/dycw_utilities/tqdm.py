from collections.abc import Iterable
from collections.abc import Mapping
from io import StringIO
from io import TextIOWrapper
from typing import Any
from typing import Optional
from typing import Union

from tqdm import tqdm as _tqdm

from dycw_utilities.pytest import is_pytest


class tqdm(_tqdm):
    def __init__(
        self,
        iterable: Optional[Iterable[Any]] = None,
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
    ) -> None:
        super().__init__(
            iterable=iterable,
            desc=desc,
            total=total,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=mininterval,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            disable=is_pytest(),
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
