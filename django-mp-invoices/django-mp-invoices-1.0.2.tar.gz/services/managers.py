
from django.db import models

from services.querysets import ServiceItemQuerySet


class ServiceItemManager(models.Manager):

    def get_queryset(self):
        return ServiceItemQuerySet(self.model, using=self._db)

    def search(self, **kwargs):
        return self.get_queryset().search(**kwargs)
