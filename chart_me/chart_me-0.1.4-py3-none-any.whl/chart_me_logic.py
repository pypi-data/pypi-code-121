"""contains core chart_me function """
# Standard library imports
from typing import List, Type

# Third party imports
import pandas as pd

# chart_me imports
from chart_me.chart_configs import ChartConfig


def chart_me(
    df: pd.DataFrame, *col_args: str, chart_confs: Type[ChartConfig] = ChartConfig
) -> None:
    """validates, infers data type, assembles and displays charts

    Args:
        df: pandas dataframe
        cols_args: position only collection of column names to render # TODO-(ptrn)
        chart_confs: Manages all settings for Chart creations. Defaults to
            chart_config.ChartConfig -vdefines three classes validate_column_strategy,
            datatype_infer_strategy, assemble_charts_strategy

    Raises:
        ValueError: check number of columns
    """

    cols: List[str] = list(col_args)
    if cols:
        for c in cols:
            # will raise an error if insufficient
            chart_confs.validate_column_strategy(df, c).validate_column()

        # get inferred datatypes
        infer = chart_confs.datatype_infer_strategy(df, cols)
        infer_dtypes = infer.infer_datatypes()

        # get charting strategy
        assembler = chart_confs.assemble_charts_strategy(df, cols, infer_dtypes)
        charts_ = assembler.assemble_charts()
        for c in charts_:
            c.display()

    else:
        raise ValueError("need to send a least one column")
