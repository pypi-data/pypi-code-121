import openride
import pytest



def test_init():
    s = openride.Size(1,2,3)
    assert s.x == 1
    assert s.y == 2
    assert s.z == 3


def test_post_init_fail():
    with pytest.raises(ValueError):
        openride.Size(-1)