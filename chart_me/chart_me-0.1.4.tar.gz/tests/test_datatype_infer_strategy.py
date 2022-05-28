# Third party imports
import pytest

# chart_me imports
import chart_me.datatype_infer_strategy as dti
from chart_me.datatype_infer_strategy import (
    ChartMeDataType,
    ChartMeDataTypeMetaType,
    InferedDataTypes,
)

# preagg_inputs = "cols,output"
# preagg_checks =


@pytest.mark.parametrize(
    "pa_cols, pa_output",
    [
        ("unique_vals", True),
        ("unique_with_nulls", False),
        ("duplicates", False),
        ("unique_vals,duplicates", True),
    ],
)
def test_preagg_checks(conftest_check_agg_dataframe, pa_cols, pa_output):
    cols = list(pa_cols.split(","))
    df = conftest_check_agg_dataframe[cols]
    infer = dti.InferDataTypeStrategyDefault(df, cols)
    assert infer._check_if_preaggregated_data() is pa_output


def test_preagg_checks_too_big(conftest_check_agg_dataframe_too_big):
    df = conftest_check_agg_dataframe_too_big
    cols = ["unique_vals"]
    infer = dti.InferDataTypeStrategyDefault(df, cols)
    assert infer._check_if_preaggregated_data() is False


def test_infer_data_types(ct_df_check_infer_dtypes):
    df = ct_df_check_infer_dtypes
    cols = ct_df_check_infer_dtypes.columns.tolist()
    # chart_me imports
    from chart_me.datatype_infer_strategy import InferDataTypeStrategyDefault

    infer = InferDataTypeStrategyDefault(df, cols)
    results = infer._get_raw_data_infer_type()
    print(results)
    expected = {
        "inty_integers": ChartMeDataType.INTEGER,
        "inty_integers_w_nulls": ChartMeDataType.FLOATS,
        "floaty_floats": ChartMeDataType.FLOATS,
        "stringy_strings": ChartMeDataType.NOMINAL,
        "stringy_strings_w_nulls": ChartMeDataType.NOMINAL,
        "datie_dates": ChartMeDataType.TEMPORAL,
        "datie_dates_null": ChartMeDataType.TEMPORAL,
        "boolie_bools": ChartMeDataType.INTEGER,
        "boolie_bools_null": ChartMeDataType.INTEGER,  # * This is interesting result
    }
    assert results == expected


def test_calculate_override_data_infer_type(ct_df_override_dtypes):
    df = ct_df_override_dtypes
    cols = df.columns.tolist()
    # chart_me imports
    from chart_me.datatype_infer_strategy import InferDataTypeStrategyDefault

    infer = InferDataTypeStrategyDefault(df, cols)
    _ = infer._get_raw_data_infer_type()
    results = infer._calculate_override_data_infer_type()
    expected = {
        "stringy_dates": ChartMeDataType.TEMPORAL,
        "inty_integers_w_nulls": ChartMeDataType.INTEGER,
        "floaty_integers": ChartMeDataType.INTEGER,
        "string_not_dates": ChartMeDataType.NOMINAL,
    }
    assert results == expected


def test_calculate_data_type_meta(ct_df_calculate_meta_dtypes):
    df = ct_df_calculate_meta_dtypes
    cols = df.columns.tolist()
    # chart_me imports
    from chart_me.datatype_infer_strategy import InferDataTypeStrategyDefault

    infer = InferDataTypeStrategyDefault(df, cols, cardinality_threshold_ratio=0.4)
    _ = infer._get_raw_data_infer_type()
    _ = infer._calculate_override_data_infer_type()
    results = infer._calculate_data_type_meta()
    expected = {
        "temporal_t": ChartMeDataTypeMetaType.TEMPORAL,
        "floaties_q": ChartMeDataTypeMetaType.QUANTITATIVE,
        "nominal_lc": ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
        "nominal_hc": ChartMeDataTypeMetaType.CATEGORICAL_HIGH_CARDINALITY,
        "nominal_k": ChartMeDataTypeMetaType.KEY,
        "integers_b": ChartMeDataTypeMetaType.BOOLEAN,
        "integers_k": ChartMeDataTypeMetaType.KEY,
        "integers_q": ChartMeDataTypeMetaType.QUANTITATIVE,
    }
    print(results)
    assert results == expected


def test_infer_datatype_function_has_protocol(ct_df_calculate_meta_dtypes):
    df = ct_df_calculate_meta_dtypes
    cols = df.columns.tolist()
    # chart_me imports
    from chart_me.datatype_infer_strategy import InferDataTypeStrategyDefault

    infer = InferDataTypeStrategyDefault(df, cols, cardinality_threshold_ratio=0.4)
    infer_type = infer.infer_datatypes()
    assert isinstance(infer_type, InferedDataTypes)


def test_infer_datatype_function_right_values(ct_df_calculate_meta_dtypes):
    df = ct_df_calculate_meta_dtypes
    cols = df.columns.tolist()
    # chart_me imports
    from chart_me.datatype_infer_strategy import InferDataTypeStrategyDefault

    infer = InferDataTypeStrategyDefault(df, cols, cardinality_threshold_ratio=0.4)
    infer_type = infer.infer_datatypes()
    expect = InferedDataTypes(
        preaggregated=True,
        chart_me_data_types={
            "temporal_t": ChartMeDataType.TEMPORAL,
            "integers_b": ChartMeDataType.INTEGER,
            "integers_q": ChartMeDataType.INTEGER,
            "integers_k": ChartMeDataType.INTEGER,
            "floaties_q": ChartMeDataType.FLOATS,
            "nominal_lc": ChartMeDataType.NOMINAL,
            "nominal_hc": ChartMeDataType.NOMINAL,
            "nominal_k": ChartMeDataType.NOMINAL,
        },
        chart_me_data_types_meta={
            "temporal_t": ChartMeDataTypeMetaType.TEMPORAL,
            "integers_b": ChartMeDataTypeMetaType.BOOLEAN,
            "integers_q": ChartMeDataTypeMetaType.QUANTITATIVE,
            "integers_k": ChartMeDataTypeMetaType.KEY,
            "floaties_q": ChartMeDataTypeMetaType.QUANTITATIVE,
            "nominal_lc": ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
            "nominal_hc": ChartMeDataTypeMetaType.CATEGORICAL_HIGH_CARDINALITY,
            "nominal_k": ChartMeDataTypeMetaType.KEY,
        },
    )
    print(infer_type)
    assert expect == infer_type
