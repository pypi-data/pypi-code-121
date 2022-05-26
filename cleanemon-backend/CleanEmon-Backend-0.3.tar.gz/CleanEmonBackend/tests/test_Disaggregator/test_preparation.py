from CleanEmonBackend.Disaggregator.preparation import energy_data_to_dataframe


def test_energy_data_to_dataframe(energy_data):
    old_cols = energy_data.energy_data[0].keys()
    df = energy_data_to_dataframe(energy_data)

    assert len(df.columns) == len(old_cols) + 1
    assert df.shape[0] == 17280
    assert any([("original" in col) for col in df.columns])
