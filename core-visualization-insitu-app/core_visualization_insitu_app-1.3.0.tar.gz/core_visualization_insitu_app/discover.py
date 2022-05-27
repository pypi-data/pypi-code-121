""" Auto discovery of Insitu Visualization app.
"""
from django.core.exceptions import ObjectDoesNotExist
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from core_visualization_insitu_app.tasks import build_visualization_data


def init_periodic_tasks():
    """Create periodic tasks for the app and add them to a crontab schedule"""
    # Execute daily at midnight
    schedule, _ = CrontabSchedule.objects.get_or_create(
        hour=0,
        minute=0,
    )
    try:
        PeriodicTask.objects.get(name=build_visualization_data.__name__)
    except ObjectDoesNotExist:
        PeriodicTask.objects.create(
            crontab=schedule,
            name=build_visualization_data.__name__,
            task="core_visualization_insitu_app.tasks.build_visualization_data",
        )
