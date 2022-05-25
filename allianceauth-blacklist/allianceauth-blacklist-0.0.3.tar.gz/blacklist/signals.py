from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from . import tasks
# signals go here

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.EveNote)
def process_eve_note(sender, instance: models.EveNote, *args, **kwargs):
    if instance.pk:
        tasks.run_blacklist_update.apply_async(priority=3, args=[instance.pk])
