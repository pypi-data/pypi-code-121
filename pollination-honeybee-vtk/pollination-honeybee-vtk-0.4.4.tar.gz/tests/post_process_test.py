from pollination.honeybee_vtk.post_process import Gif, TransparentImages
from queenbee.plugin.function import Function


def test_gif():
    function = Gif().queenbee
    assert function.name == 'gif'
    assert isinstance(function, Function)


def test_transparent_images():
    function = TransparentImages().queenbee
    assert function.name == 'transparent-images'
    assert isinstance(function, Function)
