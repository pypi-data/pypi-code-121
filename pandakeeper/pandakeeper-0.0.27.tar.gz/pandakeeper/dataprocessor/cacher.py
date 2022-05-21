from typing import Optional

from pandas import DataFrame
from typing_extensions import final

from pandakeeper.dataprocessor import DataProcessor

__all__ = (
    'DataCacher',
    'RuntimeCacher',
    'SingleInputRuntimeCacher',
)


class DataCacher(DataProcessor):
    """Abstract DataProcessor that caches input data."""
    __slots__ = ()

    @final
    @property
    def use_cached(self) -> bool:
        return True


class RuntimeCacher(DataCacher):
    """Abstract DataCacher for caching Node outputs to RAM."""
    __slots__ = ('__dataframe',)
    __dataframe: Optional[DataFrame]

    @final
    def _dump_to_cache(self, data: DataFrame) -> None:
        self.__dataframe = data

    @final
    def _clear_cache_storage(self) -> None:
        self.__dataframe = None

    @final
    def _load_cached(self) -> DataFrame:
        df = self.__dataframe
        if df is not None:
            return df
        raise ValueError("Cannot load non-cached data")


class SingleInputRuntimeCacher(RuntimeCacher):
    """RuntimeCacher for caching single input Node."""
    __slots__ = ()

    def _load_non_cached(self) -> DataFrame:
        pnc = self.positional_input_nodes
        nnc = self.named_input_nodes
        total_dfs = len(nnc) + len(pnc)
        if total_dfs != 1:
            raise ValueError(
                "Cannot be connected to more or less than one Node. "
                f"Actual number of connections: {total_dfs}"
            )
        try:
            node_connection = pnc[0]
        except IndexError:
            node_connection = next(iter(nnc.values()))
        return node_connection.extract_data()

    def transform_data(self, data: DataFrame) -> DataFrame:
        return data
