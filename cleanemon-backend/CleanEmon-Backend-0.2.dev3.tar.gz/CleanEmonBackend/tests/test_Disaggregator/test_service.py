import pytest

from CleanEmonBackend.Disaggregator.service import update


@pytest.mark.skip
def test_update():
    update("2022-05-14")
