import pytest


@pytest.mark.solarsystem
@pytest.mark.xfail
def test_load_kernels():
    assert False