import os
import pytest

from pycarta.api import create_agent

@pytest.fixture
def cartaAuth():
    if "CARTA_AUTH" not in os.environ:
        print("Set 'export CARTA_AUTH=[Carta auth token]' before testing.")
        raise ValueError(
            "Environment variable CARTA_AUTH must be set to run tests."
        )
    return os.environ["CARTA_AUTH"]


@pytest.fixture
def cartaUrl():
    return os.environ.get("CARTA_URL", "https://localhost:5001/api")


@pytest.fixture
def agent(cartaAuth, cartaUrl):
    return create_agent(
        cartaAuth,
        url=cartaUrl
    )
