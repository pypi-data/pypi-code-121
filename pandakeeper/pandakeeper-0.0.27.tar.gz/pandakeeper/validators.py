from pandera import DataFrameSchema
from typing_extensions import Final

__all__ = (
    'AnyDataFrame',
)

AnyDataFrame: Final = DataFrameSchema()
