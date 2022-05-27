""" Auto discovery of Schema Viewer app.
"""
from django.core.exceptions import ObjectDoesNotExist
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from core_schema_viewer_app.tasks import delete_old_sandbox_data_structures


def init_periodic_tasks():
    """Create periodic tasks for the app and add them to a crontab schedule"""
    # Execute daily at midnight
    schedule, _ = CrontabSchedule.objects.get_or_create(
        hour=0,
        minute=0,
    )
    try:
        PeriodicTask.objects.get(name=delete_old_sandbox_data_structures.__name__)
    except ObjectDoesNotExist:
        PeriodicTask.objects.create(
            crontab=schedule,
            name=delete_old_sandbox_data_structures.__name__,
            task="core_schema_viewer_app.tasks.delete_old_sandbox_data_structures",
        )
