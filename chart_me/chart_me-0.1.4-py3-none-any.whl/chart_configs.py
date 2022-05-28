"""Defines default Chart Config"""

# Standard library imports
from dataclasses import dataclass
from typing import Type

# chart_me imports
from chart_me.charting_assembly_strategy import (
    AssembleChartsStrategy,
    AssembleChartsStrategyDefault,
)
from chart_me.data_validation_strategy import (
    ValidateColumnStrategy,
    ValidateColumnStrategyDefault,
)
from chart_me.datatype_infer_strategy import (
    InferDataTypeStrategy,
    InferDataTypeStrategyDefault,
)


@dataclass
class ChartConfig:
    """Default Instance of Chart Config"""

    validate_column_strategy: Type[
        ValidateColumnStrategy
    ] = ValidateColumnStrategyDefault
    datatype_infer_strategy: Type[InferDataTypeStrategy] = InferDataTypeStrategyDefault
    assemble_charts_strategy: Type[
        AssembleChartsStrategy
    ] = AssembleChartsStrategyDefault
