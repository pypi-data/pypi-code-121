
import logging

from django.core.cache import cache
from django.db.models import Manager
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class CacheableMixin:
    CACHE = cache
    CACHED_PROPERTIES = []

    @classmethod
    def cache_key(cls, pk):
        return f"pfx.{cls._meta.db_table}.{pk}"

    @classmethod
    def cache_get(cls, pk):
        return cls.CACHE.get(cls.cache_key(pk))

    def cache(self):
        self.load_cached_properties()
        self.CACHE.set(self.cache_key(self.pk), self)

    @classmethod
    def cache_delete_by_pk(cls, pk):
        cls.CACHE.delete(cls.cache_key(pk))

    def cache_delete(self):
        self.cache_delete_by_pk(self.pk)

    def refresh_from_db(self, using=None, fields=None):
        super().refresh_from_db(using, fields)
        self.cache_delete()

    def load_cached_properties(self):
        for prop in self.CACHED_PROPERTIES:
            getattr(self, prop)


class CacheDependsMixin:
    CACHE_DEPENDS_FIELDS = []

    def _process_attr(self, attr, *rest):
        if isinstance(attr, Manager):
            for a in attr.all():
                self._process_attr(a, *rest)
        elif rest:
            self._cache_delete_depends(attr, *rest)
        elif attr:
            attr.cache_delete()

    def _cache_delete_depends(self, obj, field, *rest):
        attr = getattr(obj, field)
        self._process_attr(attr, *rest)

    def cache_delete_depends(self):
        for field in self.CACHE_DEPENDS_FIELDS:
            self._cache_delete_depends(self, *field.split('.'))


@receiver(post_save)
def post_save_cache(sender, instance, **kwargs):
    if issubclass(sender, CacheableMixin):
        instance.cache_delete()
    if issubclass(sender, CacheDependsMixin):
        instance.cache_delete_depends()


@receiver(pre_delete)
def pre_delete_cache(sender, instance, **kwargs):
    if issubclass(sender, CacheableMixin):
        instance.cache_delete()
    if issubclass(sender, CacheDependsMixin):
        instance.cache_delete_depends()
