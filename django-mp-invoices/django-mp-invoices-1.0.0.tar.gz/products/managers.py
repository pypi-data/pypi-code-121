
from django.db import models

from products.querysets import ProductQuerySet


class ProductManager(models.Manager):

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def search(self, **kwargs):
        return self.get_queryset().search(**kwargs)

    def active(self):
        return self.get_queryset().active()
