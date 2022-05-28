"""Specify AssembleChartsStrategy Protocol; Default Implementation of Chart Assembly

The AssembleChartsStrategy Protocal requires one method - assemble_charts that return
a list of High Level Altair Charts or Compound Chart. The AssembleChartStrategy expects
two MetaData Objects InferedDataTypes that specificy metadata about columns in the
dataframe.

    Typical usage example:

    assembler = AssembleChartsStrategyDefault(df, cols, infer_dtypes)
    charts = assembler.assemble_charts()
"""
# Standard library imports
import sys
from typing import List, Union

if sys.version_info >= (3, 8):
    # Standard library imports
    from typing import Protocol
else:
    from typing_extensions import Protocol

# Standard library imports
import warnings

# Third party imports
import altair as alt
import pandas as pd

# chart_me imports
from chart_me.datatype_infer_strategy import ChartMeDataType, InferedDataTypes
from chart_me.errors import InsufficientValidColumnsError

from .bivariate import assemble_bivariate_charts
from .univariate import assemble_univariate_charts


class AssembleChartsStrategy(Protocol):
    """Defines the protocol type for AssembleChartsStrategy

    Protocal requires 1 method --- assemble_charts
    """

    def assemble_charts(self) -> List[Union[alt.Chart, alt.HConcatChart]]:
        """Defines Protocal Type for AssembleChartsStrategy

        Args:
            df (pd.DataFrame):
            cols (List[str]): at least 1 and no more then 2 at this time
            infered_data_types (InferedDataTypes): metadata required to guide viz logic

        Returns:
            List[Union[alt.Chart, alt.HConcatChart]]: return a list of Altair visuals
        """


class AssembleChartsStrategyDefault:
    """Default implementation of AssembleChartsStrategy

    Default implementation strategy provided by chart_me. The core logic is
    provided by seperate modules depending on number of columns provided - so far
    2 are build univariate & bivariate. More then 2 columns will throw an error
    """

    def __init__(
        self,
        df: pd.DataFrame,
        cols: List[str],
        infered_data_types: InferedDataTypes,
        **kwargs,
    ) -> None:
        """Init Default Assemble Charts Strategy Object

        Args:
            df: dataframe
            cols: column names at least 1 and no more then 2 at this time
            infered_data_types: An InferedDataTypes instance containing metadata
            required to guide Altair rules
        """
        self.df = df
        self.user_provided_cols = cols
        self.preaggreted_fl = infered_data_types.preaggregated
        self.infered_data_types = infered_data_types
        self.__dict__.update(kwargs)

    def assemble_charts(self) -> List[Union[alt.Chart, alt.HConcatChart]]:
        """assembles charts based on columns count

        Returns:
            A list of Altair Chart/Compound charts to display

        Raises:
            InsufficientValidColumnsError: Will occur if no columns available after
                removing unsupported types.
            NotImplementedError: Only support 1 or 2 columns at this time

        """

        self.supported_cols: List[Union[alt.Chart, alt.HConcatChart]] = []
        # logic is predicated on number of columns & preaggregated status
        for c in self.user_provided_cols:
            if (
                self.infered_data_types.chart_me_data_types[c]
                == ChartMeDataType.NOT_SUPPORTED_TYPE
            ):
                warnings.warn(f"{c}-is not a supported datatype - ignoring")
            else:
                self.supported_cols.append(c)
        if not len(self.supported_cols):
            raise InsufficientValidColumnsError(
                "There's no columns with supported DataType"
            )
        elif len(self.supported_cols) == 1:
            charts = assemble_univariate_charts(
                self.df, self.supported_cols, self.infered_data_types
            )
        elif len(self.supported_cols) == 2:
            charts = assemble_bivariate_charts(
                self.df, self.supported_cols, self.infered_data_types
            )
        else:
            raise NotImplementedError("Only support two columns at this time")
        return charts
