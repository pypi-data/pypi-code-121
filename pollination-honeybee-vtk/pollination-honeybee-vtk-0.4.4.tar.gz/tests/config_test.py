from pollination.honeybee_vtk.config import TimeStepData
from queenbee.plugin.function import Function


def test_time_step_data():
    function = TimeStepData().queenbee
    assert function.name == 'time-step-data'
    assert isinstance(function, Function)
