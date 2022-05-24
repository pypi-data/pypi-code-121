from typing import Any, Callable, Iterable, Optional

import numpy as np
from joblib import Parallel, delayed

from ._typing import FilePath


def execute_parallel(
    function: Callable[[FilePath, FilePath], None],
    srcs: Iterable[FilePath],
    dsts: Iterable[FilePath],
    *,
    n_jobs: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Execute function in parallel."""

    delayed_function = delayed(function)
    with Parallel(n_jobs=n_jobs, **kwargs) as parallel:
        parallel(delayed_function(src, dst) for src, dst in zip(srcs, dsts))


def reduce_parallel(
    function: Callable[[FilePath], np.ndarray],
    srcs: Iterable[FilePath],
    *,
    n_jobs: Optional[int] = None,
    **kwargs: Any,
) -> np.ndarray:
    """Reduce function in parallel."""

    delayed_function = delayed(function)
    with Parallel(n_jobs=n_jobs, **kwargs) as parallel:
        result = parallel(delayed_function(src) for src in srcs)
    return np.stack(result)
