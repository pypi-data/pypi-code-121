"""Module containing _BaseSource class.

_BaseSource is the abstract data source class from which all concrete data sources
must inherit.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import inspect
import logging
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    TypeVar,
    Union,
)

import methodtools
from mypy_extensions import Arg, DefaultNamedArg, KwArg, VarArg
import numpy as np
import pandas as pd

from bitfount.data.datasources.utils import _modify_column, _modify_file_paths
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.exceptions import DataNotLoadedError
from bitfount.data.types import (
    DataPathModifiers,
    _Column,
    _GetColumnCallable,
    _GetDtypesCallable,
)
from bitfount.data.utils import _generate_dtypes_hash, _hash_str
from bitfount.types import _Dtypes
from bitfount.utils import seed_all

logger = logging.getLogger(__name__)


T = TypeVar("T", bound="_BaseSource")
_BaseSourceInitSignature = Callable[
    [
        Arg(T, "self"),  # noqa: F821
        VarArg(Any),
        DefaultNamedArg(Optional[DatasetSplitter], "data_splitter"),  # noqa: F821
        DefaultNamedArg(Optional[int], "seed"),  # noqa: F821
        DefaultNamedArg(
            Optional[Dict[str, DataPathModifiers]], "modifiers"  # noqa: F821
        ),
        DefaultNamedArg(Union[str, Sequence[str], None], "ignore_cols"),  # noqa: F821
        KwArg(Any),
    ],
    None,
]


class _BaseSource(ABC):
    """Abstract Base Source from which all other data sources must inherit.

    Args:
        data_splitter: Approach used for splitting the data into training, test,
            validation. Defaults to None.
        seed: Random number seed. Used for setting random seed for all libraries.
            Defaults to None.
        modifiers: Dictionary used for modifying paths/ extensions in the dataframe.
            Defaults to None.
        ignore_cols: Column/list of columns to be ignored from the data.
            Defaults to None.

    Attributes:
        data: A Dataframe-type object which contains the data.
        data_splitter: Approach used for splitting the data into training, test,
            validation.
        seed: Random number seed. Used for setting random seed for all libraries.
        train_idxs: A numpy array containing the indices of the data which
            will be used for training.
        validation_idxs: A numpy array containing the indices of the data which
            will be used for validation.
        test_idxs: A numpy array containing the indices of the data which
            will be used for testing.

    """

    def __init__(
        self,
        *args: Any,
        data_splitter: Optional[DatasetSplitter] = None,
        seed: Optional[int] = None,
        modifiers: Optional[Dict[str, DataPathModifiers]] = None,
        ignore_cols: Optional[Union[str, Sequence[str]]] = None,
        **kwargs: Any,
    ) -> None:
        self.data_splitter = data_splitter
        self.seed = seed
        self._modifiers = modifiers
        self._data_is_split: bool = False
        self._data_is_loaded: bool = False
        seed_all(self.seed)

        self._train_idxs: Optional[np.ndarray] = None
        self._validation_idxs: Optional[np.ndarray] = None
        self._test_idxs: Optional[np.ndarray] = None

        self._data: pd.DataFrame
        self._table_hashes: Set[str] = set()

        self._ignore_cols: List[str] = []
        if isinstance(ignore_cols, str):
            self._ignore_cols = [ignore_cols]
        elif ignore_cols is not None:
            self._ignore_cols = list(ignore_cols)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        # Call _BaseSource __init__ when initialising subclass
        cls.__init__ = cls.init_subclass()  # type: ignore[assignment] # reason: wrap subclass __init__ # noqa: B950

        if not (inspect.isabstract(cls) or ABC in cls.__bases__):
            cls.get_dtypes = cls._get_dtypes()  # type: ignore[assignment] # reason: wrap subclass get_dtypes # noqa: B950
            cls.get_column = cls._get_column()  # type: ignore[assignment] # reason: wrap subclass get_column # noqa: B950

    @classmethod
    def init_subclass(
        cls,
    ) -> _BaseSourceInitSignature:
        """Decorate subclass __init__ to call super class __init__ .

        Force all data sources to call super class __init__ to set required attributes.
        """
        subclass_init = cls.__init__

        def __init__(
            self: _BaseSource,
            *args: Any,
            data_splitter: Optional[DatasetSplitter] = None,
            seed: Optional[int] = None,
            modifiers: Optional[Dict[str, DataPathModifiers]] = None,
            ignore_cols: Optional[Union[str, Sequence[str]]] = None,
            **kwargs: Any,
        ) -> None:
            _BaseSource.__init__(
                self,
                *args,
                data_splitter=data_splitter,
                seed=seed,
                modifiers=modifiers,
                ignore_cols=ignore_cols,
                **kwargs,
            )
            subclass_init(self, *args, **kwargs)

        return __init__

    @classmethod
    def _get_dtypes(cls) -> _GetDtypesCallable:
        """Decorate subclass' get_dtypes implementation.

        Decorate subclass' implementation of get_dtypes to handle ignored
        columns and handle `_table_hashes`.
        """
        subclass_get_dtypes = cls.get_dtypes

        def get_dtypes(self: _BaseSource, **kwargs: Any) -> _Dtypes:
            dtypes: _Dtypes = subclass_get_dtypes(self, **kwargs)
            if self._ignore_cols:
                for col in self._ignore_cols:
                    if col in dtypes:
                        del dtypes[col]
            self._table_hashes.add(_generate_dtypes_hash(dtypes))
            return dtypes

        return get_dtypes

    @classmethod
    def _get_column(
        cls,
    ) -> _GetColumnCallable:
        """Decorate subclass' get_column implementation.

        Decorate subclass' implementation of get_column to handle ignored
        columns and modifiers.
        """
        subclass_get_column = cls.get_column

        def get_column(self: _BaseSource, col_name: str, **kwargs: Any) -> _Column:

            column = subclass_get_column(self, col_name, **kwargs)
            if self._modifiers:
                if modifier_dict := self._modifiers.get(col_name):
                    column = _modify_column(column, modifier_dict)
            return column

        return get_column

    @property
    def data(self) -> pd.DataFrame:
        """Data."""
        if hasattr(self, "_data"):
            return self._data
        else:
            raise DataNotLoadedError(
                "Data is not loaded yet. Please call `load_data` first."
            )

    @data.setter
    def data(self, _data: Optional[pd.DataFrame]) -> None:
        """Data setter."""
        if _data is not None:
            if isinstance(_data, pd.DataFrame):

                if self._ignore_cols:
                    # If columns already ignored in data, ignore errors.
                    _data = _data.drop(columns=self._ignore_cols, errors="ignore")
                self._data = _data

                if self._modifiers:
                    _modify_file_paths(self._data, self._modifiers)

                self._data_is_loaded = True
            else:
                raise TypeError(
                    "Invalid data attribute. "
                    "Expected pandas dataframe for attribute 'data' "
                    f"but received :{type(_data)}"
                )

    @property
    def hash(self) -> str:
        """The hash associated with this _BaseSource.

        This is the hash of the static information regarding the underlying DataFrame,
        primarily column names and content types but NOT anything content-related
        itself. It should be consistent across invocations, even if additional data
        is added, as long as the DataFrame is still compatible in its format.

        Returns:
            The hexdigest of the DataFrame hash.
        """
        if not self._table_hashes:
            raise DataNotLoadedError(
                "Data is not loaded yet. Please call `get_dtypes` first."
            )
        else:
            return _hash_str(str(sorted(self._table_hashes)))

    @abstractmethod
    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Implement this method to get distinct values from list of columns."""
        raise NotImplementedError

    @abstractmethod
    def get_column(self, col_name: str, **kwargs: Any) -> _Column:
        """Implement this method to get single column from dataset."""
        raise NotImplementedError

    # TODO: [BIT-1780] Simplify referencing data in _BaseSource
    # We want to avoid recalculating but we dont want to cache more
    # than one result at a time to save memory
    @methodtools.lru_cache(maxsize=1)  # type: ignore[misc]  # Reason: methodtools untyped  # noqa: B950
    @abstractmethod
    def get_data(self, **kwargs: Any) -> Optional[pd.DataFrame]:
        """Implement this method to loads and return dataset."""
        raise NotImplementedError

    @abstractmethod
    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Implement this method to get the columns and column types from dataset."""
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Implement this method to get the number of rows in the dataset."""
        raise NotImplementedError

    @property
    @abstractmethod
    def multi_table(self) -> bool:
        """Implement this method to define whether the data source is mulit-table."""
        raise NotImplementedError

    def load_data(self, **kwargs: Any) -> None:
        """Load the data for the datasource.

        We wrap get_data with lru_cache so this method is idempotent so it
        can be called multiple times with the same arguments without reloading
        the data.

        Raises:
            TypeError: If data format is not supported.
        """
        data = self.get_data(**kwargs)
        if data is not None:
            self.data = data


class _MultiTableSource(_BaseSource, ABC):
    """Abstract base source that supports multiple tables."""

    @property
    @abstractmethod
    def table_names(self) -> List[str]:
        """Implement this method to define whether the data source is multi-table."""
        raise NotImplementedError
