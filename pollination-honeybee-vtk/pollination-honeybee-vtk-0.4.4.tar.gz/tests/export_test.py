from pollination.honeybee_vtk.export import ModelImages, GridImages, TimeStepImages
from queenbee.plugin.function import Function


def test_model_images():
    function = ModelImages().queenbee
    assert function.name == 'model-images'
    assert isinstance(function, Function)


def test_grid_images():
    function = GridImages().queenbee
    assert function.name == 'grid-images'
    assert isinstance(function, Function)


def test_time_step_images():
    function = TimeStepImages().queenbee
    assert function.name == 'time-step-images'
    assert isinstance(function, Function)
