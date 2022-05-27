from pollination.honeybee_energy.result import AvailableResultsInfo, DataByOutput, \
    ResultCsvQueryable, EnergyUseIntensity, ZoneSizes, ComponentSizes
from queenbee.plugin.function import Function


def test_energy_use_intensity():
    function = EnergyUseIntensity().queenbee
    assert function.name == 'energy-use-intensity'
    assert isinstance(function, Function)


def test_available_results_info():
    function = AvailableResultsInfo().queenbee
    assert function.name == 'available-results-info'
    assert isinstance(function, Function)


def test_data_by_output():
    function = DataByOutput().queenbee
    assert function.name == 'data-by-output'
    assert isinstance(function, Function)


def test_zone_sizes():
    function = ZoneSizes().queenbee
    assert function.name == 'zone-sizes'
    assert isinstance(function, Function)


def test_component_sizes():
    function = ComponentSizes().queenbee
    assert function.name == 'component-sizes'
    assert isinstance(function, Function)


def test_result_csv_queryable():
    function = ResultCsvQueryable().queenbee
    assert function.name == 'result-csv-queryable'
    assert isinstance(function, Function)
