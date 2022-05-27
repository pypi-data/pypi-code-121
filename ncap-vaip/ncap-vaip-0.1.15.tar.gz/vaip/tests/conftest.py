import os

import pytest
from pathlib import Path


@pytest.fixture(scope='class')
def fixtures(request):
    """
    Provides paths that are used across tests to make things simpler.
    :param request: Can also hold variables instead of yielding.
        See metadata-models.
    :return: Yields objects to use.
    """
    tests_dir = os.path.dirname(__file__)
    fixtures_dir = os.path.join(
        tests_dir,
        'fixtures'
    )

    fixtures_dir = os.path.join(
        tests_dir,
        'fixtures'
    )

    yield {
        "tests_dir": tests_dir,
        "fixtures_dir": fixtures_dir,
    }

