"""Module defines a core enums, protocal and default  datatype infer strategy

Defines 2 Enum -> ChartMeDataType & ChartMeDataTypeMetaType the normalize
metadata. Additionally, defines the 'InferedDataTypes' that get referenced
downstream to the assembler

    Typical usage example:

    infer = InferDataTypeStrategyDefault.datatype_infer_strategy(df, cols)
    infer_dtypes = infer.infer_datatypes() #return an InferedDataTypes
"""

# Standard library imports
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    # Standard library imports
    from typing import Protocol
else:
    # Third party imports
    from typing_extensions import Protocol

# TODO think about a reorganizing into seperate module
# Standard library imports
from enum import Enum

# Third party imports
import pandas as pd


class ChartMeDataType(Enum):
    """Defines Normalized Datatypes"""

    FLOATS = "F"  # -> Metrics Avg/Media, etc...
    INTEGER = "I"  # -> Hybrid Datatypes Numerical or seen As Categorical
    TEMPORAL = ("T",)  # -> this lead to 'O' otherwise use
    NOMINAL = ("N",)
    NOT_SUPPORTED_TYPE = "NA"


class ChartMeDataTypeMetaType(Enum):
    """Defines Normalized Metadata about Datatypes

    Defines Key, Boolean, Quantitative, Categorical High Cardinality,
    Categorical Low Cardinality, Temporal, Not Supported"""

    KEY = ("K",)  # -> map to CountD
    BOOLEAN = ("B",)  # -> Context Aware
    QUANTITATIVE = ("Q",)  # -> Floats
    CATEGORICAL_HIGH_CARDINALITY = ("C-HC",)  # top-k
    CATEGORICAL_LOW_CARDINALITY = ("C-LC",)
    TEMPORAL = ("T",)
    NOT_SUPPORTED_TYPE = "NA"


@dataclass
class InferedDataTypes:
    """Core Object Returned for Assembler - column level specifications"""

    preaggregated: bool
    chart_me_data_types: Dict[str, ChartMeDataType]
    chart_me_data_types_meta: Dict[str, ChartMeDataTypeMetaType]


class InferDataTypeStrategy(Protocol):
    """Defines protocol for InferDataTypeStrategy - requires infer_datatypes"""

    def infer_datatypes(self) -> InferedDataTypes:
        """Only Method Required"""
        raise NotImplementedError


class InferDataTypeStrategyDefault:
    """Default logic to specificy metadata to drive chart assembly logic"""

    def __init__(self, df: pd.DataFrame, cols: List[str], **kwargs):
        """set instances variable"""
        self.df = df
        self.cols = cols
        self.preaggregated: Optional[bool] = None
        self.__dict__.update(kwargs)
        self.col_to_cm_dtypes: Dict[str, ChartMeDataType] = {}
        self.col_to_cm_dtypes_meta: Dict[str, ChartMeDataTypeMetaType] = {}

    def _check_if_preaggregated_data(self, threshold: int = 100):
        """First check determines aggregation - influences data type"""
        if self.df.shape[0] <= threshold:
            # check if at least l column is completely unique
            self.preaggregated = (
                True if any(self.df.nunique() == self.df.shape[0]) else False
            )
        else:
            self.preaggregated = False
        return self.preaggregated

    def _get_raw_data_infer_type(self):
        """Apply *some* burden on user to setup DF accordingly"""
        # Third party imports
        from pandas.api.types import infer_dtype

        map_from_pd_cm = {
            "string": ChartMeDataType.NOMINAL,
            "bytes": ChartMeDataType.NOT_SUPPORTED_TYPE,
            "floating": ChartMeDataType.FLOATS,
            "integer": ChartMeDataType.INTEGER,
            "mixed-integer": ChartMeDataType.NOT_SUPPORTED_TYPE,  # TODO
            "mixed-integer-float": ChartMeDataType.FLOATS,
            "decimal": ChartMeDataType.FLOATS,
            "complex": ChartMeDataType.NOT_SUPPORTED_TYPE,
            "categorical": ChartMeDataType.NOMINAL,
            "boolean": ChartMeDataType.INTEGER,
            "datetime64": ChartMeDataType.TEMPORAL,
            "datetime": ChartMeDataType.TEMPORAL,
            "date": ChartMeDataType.TEMPORAL,
            "timedelta64": ChartMeDataType.NOMINAL,
            "timedelta": ChartMeDataType.NOMINAL,
            "time": ChartMeDataType.NOT_SUPPORTED_TYPE,
            "period": ChartMeDataType.NOMINAL,
            "mixed": ChartMeDataType.NOT_SUPPORTED_TYPE,  # inform user
            "unknown-array": ChartMeDataType.NOT_SUPPORTED_TYPE,
        }

        map_from_pd = self.df[self.cols].apply(infer_dtype).to_dict()
        self.col_to_cm_dtypes = {k: map_from_pd_cm[v] for k, v in map_from_pd.items()}
        return self.col_to_cm_dtypes

    # TODO add 'sampling' not processing over huge series
    def _calculate_override_data_infer_type(self):
        """Part to is evaluate"""
        for col, data_type in self.col_to_cm_dtypes.items():
            if data_type == ChartMeDataType.FLOATS:
                data_sans_nulls = self.df[col].dropna()
                if all(data_sans_nulls.apply(lambda x: x.is_integer())):
                    self.col_to_cm_dtypes[
                        col
                    ] = (
                        ChartMeDataType.INTEGER
                    )  # * Not casting becasause of pd.nan issue
            if data_type == ChartMeDataType.NOMINAL:
                # Third party imports
                from dateutil.parser import ParserError  # type: ignore

                try:
                    self.df[col] = pd.to_datetime(self.df[col])
                    self.col_to_cm_dtypes[col] = ChartMeDataType.TEMPORAL
                except (ParserError, TypeError, ValueError):
                    pass
        return self.col_to_cm_dtypes

    def _get_data_infer_meta_type_col(self, col: str):
        """series of evaluations"""
        if self.col_to_cm_dtypes[col] == ChartMeDataType.NOT_SUPPORTED_TYPE:
            self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.NOT_SUPPORTED_TYPE
        if self.col_to_cm_dtypes[col] == ChartMeDataType.FLOATS:
            self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.QUANTITATIVE
        if self.col_to_cm_dtypes[col] == ChartMeDataType.TEMPORAL:
            self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.TEMPORAL
        if self.col_to_cm_dtypes[col] == ChartMeDataType.INTEGER:
            # Check if a Key - All Unique and No Nulls
            if self.df[col].nunique() == self.df[col].shape[0]:
                self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.KEY
            # Check if a Boolean Value
            elif (
                int(self.df[col].min()) == 0
                and int(self.df[col].max()) == 1
                and self.df[col].nunique() == 2
            ):
                self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.BOOLEAN
            else:
                self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.QUANTITATIVE
        if self.col_to_cm_dtypes[col] == ChartMeDataType.NOMINAL:

            hc_threshold = (
                self.__dict__.get("cardinality_threshold_ratio", 0.30)
                if self.preaggregated
                else self.__dict__.get("cardinality_threshold_ratio", 0.10)
            )
            # if 100; 10 or less low cardinality
            if self.df[col].nunique() == self.df[col].shape[0]:
                self.col_to_cm_dtypes_meta[col] = ChartMeDataTypeMetaType.KEY
            elif self.df[col].nunique() / self.df.shape[0] <= hc_threshold:
                self.col_to_cm_dtypes_meta[
                    col
                ] = ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY
            else:
                self.col_to_cm_dtypes_meta[
                    col
                ] = ChartMeDataTypeMetaType.CATEGORICAL_HIGH_CARDINALITY

    def _calculate_data_type_meta(self):
        """wrapper to iterate over all columns"""
        for col, val in self.col_to_cm_dtypes.items():
            self._get_data_infer_meta_type_col(col)
        return self.col_to_cm_dtypes_meta

    def infer_datatypes(self) -> InferedDataTypes:
        """Core function of stategy is returning metadata to rendering engine

        Args:
            df (pd.DataFrame): pandas dataframe
            cols (List[str]): list of columns passed in from user

        Returns:
            InferedDataTypes: describes MetaData to engine
        """
        pre_agg_flag = self._check_if_preaggregated_data()
        _ = self._get_raw_data_infer_type()
        infered_data_type = self._calculate_override_data_infer_type()
        infered_data_type_meta = self._calculate_data_type_meta()
        self.infered_data_types = InferedDataTypes(
            pre_agg_flag, infered_data_type, infered_data_type_meta
        )
        return self.infered_data_types
