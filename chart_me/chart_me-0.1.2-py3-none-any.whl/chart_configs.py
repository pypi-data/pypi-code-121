"""Defines default Chart Config"""

from dataclasses import dataclass
from chart_me.data_validation_strategy import ValidateColumnStrategy, ValidateColumnStrategyDefault
from typing import Type
from chart_me.datatype_infer_strategy import InferDataTypeStrategy, InferDataTypeStrategyDefault
from chart_me.charting_assembly_strategy import AssembleChartsStrategy, AssembleChartsStrategyDefault
from chart_me.data_validation_strategy import ValidateColumnStrategyDefault


@dataclass
class ChartConfig:
    """Default Instance of Chart Config"""
    validate_column_strategy: Type[ValidateColumnStrategy] = ValidateColumnStrategyDefault
    datatype_infer_strategy: Type[InferDataTypeStrategy] = InferDataTypeStrategyDefault
    assemble_charts_strategy: Type[AssembleChartsStrategy] = AssembleChartsStrategyDefault

