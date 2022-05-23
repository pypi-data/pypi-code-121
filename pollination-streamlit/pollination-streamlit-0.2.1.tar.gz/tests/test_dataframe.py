import pytest
from pandas.util.testing import assert_frame_equal
from pollination_streamlit.dataframe import ColumnMeta, RunsDataFrame


@pytest.fixture
def input_columns():
    cols = ['grid-filter', 'model', 'name',
            'radiance-parameters', 'sensor-count',
            'shade_area', 'shade_count', 'shade_depth']
    cols.sort()
    return cols


@pytest.fixture
def output_columns():
    return ['results']


@pytest.fixture
def parameter_columns(input_columns):
    cols = ['grid-filter', 'name',
            'radiance-parameters', 'sensor-count',
            'shade_area', 'shade_count', 'shade_depth']
    cols.sort()
    return cols


@pytest.fixture
def artifact_columns():
    return ['model', 'results']


@pytest.fixture
def meta_columns():
    return ['job-id', 'run-id', 'run-status']


def test_column_meta(run_results_dict, input_columns,
                     output_columns,
                     parameter_columns,
                     artifact_columns,
                     meta_columns,):
    meta = ColumnMeta()
    for r in run_results_dict:
        meta.extend_from_run_result(r)

    assert meta.inputs == input_columns
    assert meta.outputs == output_columns
    assert meta.parameters == parameter_columns
    assert meta.artifacts == artifact_columns
    assert meta.meta == meta_columns


def test_create_df(run_results_dict, input_columns):
    rdf = RunsDataFrame.from_run_results(run_results_dict)

    df = rdf.dataframe

    assert_frame_equal(rdf.inputs, df[input_columns])

    assert_frame_equal(rdf.parameters, df[[
        'grid-filter', 'name',
        'radiance-parameters', 'sensor-count',
        'shade_area', 'shade_count', 'shade_depth'
    ]])
    assert_frame_equal(rdf.artifacts, df[[
        'model', 'results'
    ]])

    assert_frame_equal(rdf.meta, df[['job-id', 'run-status']])
    assert_frame_equal(rdf.outputs, df[['results']])
