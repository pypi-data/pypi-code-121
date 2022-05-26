import pytest

from CleanEmonBackend.Disaggregator.inference import disaggregate


@pytest.mark.slow
def test_disaggregate(dataframe):
    df = disaggregate(dataframe)

    assert df.shape[0] == 17280
    assert len(df.columns) > len(dataframe.columns)
