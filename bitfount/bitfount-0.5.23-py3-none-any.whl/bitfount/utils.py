"""General helpful utilities to be found here."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import importlib.util
import inspect
import logging
from pathlib import Path
import random
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    TypeVar,
    Union,
    cast,
)

import numpy as np
from sklearn.preprocessing import OneHotEncoder

__all__: List[str] = ["one_hot_encode_list", "seed_all"]

logger = logging.getLogger(__name__)

DEFAULT_SEED: int = 42


def _is_notebook() -> bool:
    """Checks if code is being executed in a notebook or not."""
    try:
        # get_ipython() is always available in a notebook, no need to import
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined] # Reason: captured by NameError # noqa: B950
        return bool(shell == "ZMQInteractiveShell")  # True if ran from Jupyter notebook
    except NameError:
        return False  # Standard Python interpreter


def seed_all(seed_value: Optional[int] = None) -> None:
    """Sets random seed for `numpy`, `python.random` and any other relevant library.

    If `pytorch` is used as the backend, this is just a wrapper around the
    `seed_everything` function from `pytorch-lightning`.

    Args:
        seed_value: The seed value to use. If None, uses the default seed (42).

    :::info

    `PYTHONHASHSEED` is not set as an environment variable because this has no effect
    once the process has been started. If you wish to set this, you should set it
    yourself in your own environment before running python.

    :::
    """
    seed_value = DEFAULT_SEED if seed_value is None else seed_value

    # Try to seed other libraries that may be present
    # Torch
    try:
        import pytorch_lightning as pl

        logger.debug(f"Setting seed of torch, random and numpy to {seed_value}")
        # This call takes care of setting the seed for all libraries including
        # random and numpy as well as pytorch. `workers=True` ensures that the workers
        # for the dataloaders are also seeded.
        pl.seed_everything(seed_value, workers=True)
    except ModuleNotFoundError:
        logger.debug(f"Setting seed of random and numpy to {seed_value}")
        random.seed(seed_value)
        np.random.seed(seed_value)


def _add_this_to_list(
    this: Union[Any, Iterable[Any]], the_list: List[Any]
) -> List[Any]:
    """Adds this to list.

    Checks if `this` is an iterable, in which case it extends the provided list
    (unless it is a string). Otherwise it appends to the provided list if not None.

    Finally, it removes duplicates from the list and returns it.
    """
    if isinstance(this, Iterable) and not isinstance(this, str):
        the_list.extend(this)
    else:
        if this is not None:
            the_list.append(this)
    return list(set(the_list))


def _array_version(this: Union[Any, Iterable[Any]]) -> List[Any]:
    """Returns this as a list.

    Checks if 'this' is an iterable, in which case it returns it as a list (unless
    it's a string), otherwise it wraps it as a single element list.
    """
    if isinstance(this, Iterable) and not isinstance(this, str):
        return list(this)
    return [this]


def one_hot_encode_list(
    targets: Union[
        np.ndarray, Iterable[np.ndarray], Iterable[int], Iterable[Iterable[int]]
    ]
) -> np.ndarray:
    """Converts a list of targets into a list of one-hot targets."""
    arr_targets: np.ndarray = np.asarray(targets)

    # Can only encode 1D or 2D targets
    if not (1 <= arr_targets.ndim <= 2):
        raise ValueError(
            f"Incorrect number of dimensions for one-hot encoding; "
            f"expected 1 or 2, got {arr_targets.ndim}"
        )

    # OneHotEncoder needs a 2D numpy array so if this is 1D, needs reshape
    if arr_targets.ndim == 1:
        arr_targets = arr_targets.reshape(-1, 1)

    # Ensure output is ndarray of correct types
    encoder = OneHotEncoder(categories="auto", sparse=False, dtype=np.uint8)
    # sparse=False guarantees output of ndarray
    return cast(np.ndarray, encoder.fit_transform(arr_targets))


def _get_non_abstract_classes_from_module(path_to_module: Path) -> Dict[str, type]:
    """Returns non-abstract classes from a module path.

    Returns a dictionary of non-abstract class names and classes present within a
    module file which is given as a Path object.
    """
    path = path_to_module.expanduser().absolute()
    module_name = path.name

    # Load the module from the file without saving it to sys.modules
    # See: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly  # noqa: B950
    spec = importlib.util.spec_from_file_location(module_name, path)
    try:
        # `spec` has type `ModuleSpec | None`. If it is None, an error is raised which
        # caught by the `try...except` block
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type] # Reason: See comment # noqa: B950
        spec.loader.exec_module(module)  # type: ignore[union-attr] # Reason: See comment # noqa: B950
    except Exception as ex:
        raise ImportError(f"Unable to load code from {path_to_module}") from ex

    classes = {
        name: class_
        for name, class_ in vars(module).items()
        if inspect.isclass(class_) and not inspect.isabstract(class_)
    }

    return classes


# TypeVars for merge_list_of_dicts
KT = TypeVar("KT")  # Key type.
VT = TypeVar("VT")  # Value type.


def _merge_list_of_dicts(
    lod: Iterable[Mapping[KT, Union[VT, Iterable[VT]]]]
) -> Dict[KT, List[VT]]:
    """Converts a list of dicts into a dict of lists.

    Each element in the dicts should be a single element or a list of elements.
    Any list of elements will be flattened into the final list, any single
    elements will be appended.

    Args:
        lod: A list of dicts to merge.

    Returns:
        A dictionary of lists where each value is the merged values from the
        input list of dicts.
    """
    # Merge into singular lists rather than a list of dicts
    merged: DefaultDict[KT, List[VT]] = defaultdict(list)

    for i in lod:
        for k, v in i.items():
            # We ignore the mypy errors on the `extend` and `append` calls because
            # we don't know the type of v. Instead rely on the `try...except` block
            # for type safety
            try:
                # Attempt to extend first (for outputs and targets)
                merged[k].extend(v)  # type: ignore[arg-type]  # Reason: will TypeError if not Iterable[VT]  # noqa: B950
            except TypeError:
                # Otherwise if not iterable, append
                v = cast(VT, v)
                merged[k].append(v)

    return merged


@dataclass
class _MegaBytes:
    """Thin wrapper for bytes->MB conversion."""

    whole: int
    fractional: float


def _get_mb_from_bytes(num_bytes: int) -> _MegaBytes:
    """Converts a number of bytes into the number of megabytes.

    Returns a tuple of the number of whole megabytes and the number of megabytes
    as a float.
    """
    mb: float = num_bytes / (1024 * 1024)
    return _MegaBytes(int(mb), mb)
