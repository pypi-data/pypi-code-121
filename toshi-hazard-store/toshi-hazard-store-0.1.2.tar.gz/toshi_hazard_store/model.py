"""This module defines the pynamodb tables used to store openquake data."""

import logging

from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute, UnicodeAttribute, VersionAttribute
from pynamodb.models import Model

from toshi_hazard_store.config import DEPLOYMENT_STAGE, IS_OFFLINE, REGION

log = logging.getLogger(__name__)


class LevelValuePairAttribute(MapAttribute):
    """Store the IMT level and the POE value at the level."""

    level = NumberAttribute(null=False)
    value = NumberAttribute(null=False)


class ToshiOpenquakeHazardCurveRlzs(Model):
    """Stores the individual hazard realisation curves."""

    class Meta:
        """DynamoDB Metadata."""

        billing_mode = 'PAY_PER_REQUEST'
        table_name = f"ToshiOpenquakeHazardCurveRlzs-{DEPLOYMENT_STAGE}"
        region = REGION
        if IS_OFFLINE:
            host = "http://localhost:8000"  # pragma: no cover

    hazard_solution_id = UnicodeAttribute(hash_key=True)
    vs30_imt_loc_rlz_rk = UnicodeAttribute(range_key=True)  # TODO: check we can actually use this in queries!

    vs30 = NumberAttribute()
    imt_code = UnicodeAttribute()
    location_code = UnicodeAttribute()
    rlz_id = UnicodeAttribute()

    lvl_val_pairs = ListAttribute(of=LevelValuePairAttribute)
    version = VersionAttribute()


class ToshiOpenquakeHazardCurveStats(Model):
    """Stores the individual hazard statistical curves."""

    class Meta:
        """DynamoDB Metadata."""

        billing_mode = 'PAY_PER_REQUEST'
        table_name = f"ToshiOpenquakeHazardCurveStats-{DEPLOYMENT_STAGE}"
        region = REGION
        if IS_OFFLINE:
            host = "http://localhost:8000"  # pragma: no cover

    hazard_solution_id = UnicodeAttribute(hash_key=True)
    vs30_imt_loc_agg_rk = UnicodeAttribute(range_key=True)

    vs30 = NumberAttribute()
    imt_code = UnicodeAttribute()
    location_code = UnicodeAttribute()
    aggregation = UnicodeAttribute()

    lvl_val_pairs = ListAttribute(of=LevelValuePairAttribute)
    version = VersionAttribute()


tables = [ToshiOpenquakeHazardCurveRlzs, ToshiOpenquakeHazardCurveStats]


def migrate():
    """Create the tables if it doesn't exist already."""
    for table in tables:
        if not table.exists():  # pragma: no cover
            table.create_table(wait=True)
            print(f"Migrate created table: {table}")
            log.info(f"Migrate created table: {table}")


def drop_tables():
    """Drop the tables if they exist."""
    for table in tables:
        if table.exists():  # pragma: no cover
            table.delete_table()
            log.info(f'deleted table: {table}')
