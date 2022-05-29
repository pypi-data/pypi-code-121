"""Factories for generating pccc objects for testing."""

import factory

from .config import Config


class ConfigFactory(factory.Factory):
    """``Config`` factory."""

    class Meta:
        """``Config`` factory configuration."""

        model = Config

    commit = ""
    config_file = "./pyproject.toml"
    header_length = 50
    body_length = factory.Faker(
        "pyint",
        min_value=50,
        max_value=120,
    )
    repair = False
    rewrap = False
    spell_check = False
    ignore_generated_commits = False
    generated_commits = []
    types = ["feat", "fix"]
    scopes = []
    footers = []
    required_footers = []
