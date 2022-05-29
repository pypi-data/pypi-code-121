from pollination.honeybee_vtk.translate import Translate
from queenbee.plugin.function import Function


def test_export_images():
    function = Translate().queenbee
    assert function.name == 'translate'
    assert isinstance(function, Function)
