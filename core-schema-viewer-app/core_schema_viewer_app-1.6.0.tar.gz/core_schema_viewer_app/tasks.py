""" Schema Viewer App tasks
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from core_schema_viewer_app.settings import SANDBOX_STRUCTURES_MAX_DAYS_IN_DATABASE
from core_schema_viewer_app.system.api import get_all_sandbox_data_structures

logger = logging.getLogger(__name__)


@shared_task
def delete_old_sandbox_data_structures():
    """Every day at midnight, delete older sandbox data structures.

    Returns:

    """
    try:
        # get older queries
        old_ds = [
            ds
            for ds in get_all_sandbox_data_structures()
            if ds.id.generation_time
            < timezone.now() - timedelta(days=SANDBOX_STRUCTURES_MAX_DAYS_IN_DATABASE)
        ]
        # remove old queries from database
        for old_data_structure in old_ds:
            logger.info(
                "Periodic task: delete sandbox data structure {}.".format(
                    str(old_data_structure.id)
                )
            )
            old_data_structure.delete()
    except Exception as e:
        logger.error(
            "An error occurred while deleting sandbox data structures ({}).".format(
                str(e)
            )
        )
