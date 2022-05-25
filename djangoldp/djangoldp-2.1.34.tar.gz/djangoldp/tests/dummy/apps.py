"""This module contains apps for testing."""

from django.apps import AppConfig

class DummyConfig(AppConfig):
    # 'djangoldp.tests' is already registered as an installed app (it simulates a LDP package)
    name = 'djangoldp.tests.dummy'
