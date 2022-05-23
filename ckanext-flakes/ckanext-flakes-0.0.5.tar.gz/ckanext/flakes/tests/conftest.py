import factory
import pytest
from ckan.tests import factories
from pytest_factoryboy import register

from ..model import Flake


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("flakes")


@register
class FlakeFactory(factories.CKANFactory):
    class Meta:
        model = Flake
        action = "flakes_flake_create"

    data = factory.Faker("pydict", value_types=(str, int))
