import pytest

from pycarta.api import create_agent

from .common_fixtures import cartaAuth, cartaUrl


def test_agent(cartaAuth, cartaUrl):
    token = cartaAuth
    url = cartaUrl
    agent = create_agent(token, url=url)
    assert agent.url == url
