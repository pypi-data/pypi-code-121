from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import FavoriteManager
from ob_dj_store.utils.model import DjangoModelCleanMixin


class Favorite(DjangoModelCleanMixin, models.Model):
    """
    Favorite model to handle user's favorites
    """

    user = models.ForeignKey(
        get_user_model(), related_name="favorites", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")
    object_id = models.PositiveIntegerField()
    # Audit fields
    created_on = models.DateTimeField(auto_now_add=True)
    objects = FavoriteManager()

    class Meta:
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")
        unique_together = (("user", "content_type", "object_id"),)

    def __str__(self):
        return "%s favorites %s" % (self.user, self.content_object)

    @classmethod
    def add_favorite(cls, content_object, user):
        content_type = ContentType.objects.get_for_model(type(content_object))
        favorite = Favorite(
            user=user,
            content_type=content_type,
            object_id=content_object.pk,
            content_object=content_object,
        )
        favorite.save()
        return favorite
