# from .feature_calculator import *
from .constants import *
import pandas as pd
from .tech_indicators import *


def get_lag_col_name(feature_col: str, lag_len: int):
    return f"Lag-{feature_col}-T-{lag_len:{DECIMAL_PLACE}}"


def get_forward_col_name(feature_col: str, fwd_len: int):
    return f"{feature_col}-Fwd_{fwd_len}"


# todo: all these need to be imported and automated
OPERATORS_IND = {RsiOperator.__name__: RsiOperator,
                 BollingerBandOperator.__name__: BollingerBandOperator,
                 AtrOperator.__name__: AtrOperator,
                 MaOperator.__name__: MaOperator,
                 VilliamrOperator.__name__: VilliamrOperator,
                 MomentomOperator.__name__: MomentomOperator,
                 WmaOperator.__name__: WmaOperator,
                 EmaOperator.__name__: EmaOperator,
                 AdxOperator.__name__: AdxOperator,
                 BopOperator.__name__: BopOperator,
                 SmaOperator.__name__: SmaOperator,
                 ReturnsOperator.__name__: ReturnsOperator,
                 MaxPriceAndReturn.__name__: MaxPriceAndReturn,
                 MinPriceAndReturn.__name__: MinPriceAndReturn,
                 ReturnVarianceOperator.__name__: ReturnVarianceOperator
                 # todo: not sure
                 # CandleStickOperators.__name__: CandleStickOperators
                 }

OPERATORS_RET = {ReturnsOperator.__name__: ReturnsOperator}

OPERATORS_FWD = {
                 ForwardHighestReturn.__name__: ForwardHighestReturn,
                 # AmplitudeBasedLabelerOperator.__name__: AmplitudeBasedLabelerOperator
                 }

def get_operator(operator_name: str):
    if operator_name in OPERATORS_IND.keys():
        col_prefix = RESULT_TECH_IND_PREFIX
        operator = OPERATORS_IND[operator_name]

    elif operator_name in OPERATORS_FWD.keys():
        col_prefix = RESULT_TECH_FWD_PREFIX
        operator = OPERATORS_FWD[operator_name]
    else:
        col_prefix = None
        operator = None

    return operator, col_prefix

class Context:
    def validate(self, data: pd.DataFrame, operators: list, periods: list, lag_periods: list = None,
                 forward_periods: list = None) -> bool:
        try:
            _ = self.get(data=data, operators=operators, periods=periods, lag_periods=lag_periods,
                         forward_periods=forward_periods)
        except Exception as e:
            print(e)
            return False

        return True

    def get(self, data: pd.DataFrame, operators: list, periods: list, lag_periods: list = None,
            forward_periods: list = None) -> pd.DataFrame:
        columns = []
        for operator in operators:
            for period in periods:
                op_columns = self.get_column_names(operator=operator, period=period, lag_periods=lag_periods,
                                               forward_periods=forward_periods)
                if set(op_columns) > set(data.columns):
                    raise Exception(f"invalid column name: operator: {operator.__name__}, period: {period}")

                columns = columns + op_columns
        result = data[columns]
        return result

    def get_column_names(self,
                         period: int,
                         operator: IndicatorOperator = None,
                         operator_name: str = None,
                         lag_periods: list = None,
                         forward_periods: list = None) -> str:

        assert lag_periods is None or forward_periods is None, "cant calculate both forwards and lags at the same time"
        columns = []

        if operator_name is None:
            operator_name = operator.__name__

        operator, col_prefix = get_operator(operator_name=operator_name)
        if operator == None:
            return None

        op_col_names = operator.get_column_names()
        for op_col_name in op_col_names:
            full_name = operator.calculate_final_column_name(prefix=col_prefix, col_name=op_col_name, period=period)
            if lag_periods:
                for lag_period in lag_periods:
                    full_name_lag = get_lag_col_name(feature_col=full_name, lag_len=lag_period)
                    columns.append(full_name_lag)
            elif forward_periods:
                for frwd_period in forward_periods:
                    full_name_fwd = get_forward_col_name(feature_col=full_name, fwd_len=frwd_period)
                    columns.append(full_name_fwd)
            else:
                columns.append(full_name)

            # columns.append(f"{col_prefix}-{op_col_name}-lag_{period}")

        return columns
