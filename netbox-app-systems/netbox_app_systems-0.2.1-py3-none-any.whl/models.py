from genericpath import exists
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.models import ChangeLoggedModel
from netbox.models.features import WebhooksMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AppSystem(NetBoxModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_app_systems:appsystem', args=[self.pk])

    class Meta:
        ordering = ['name']


class AppSystemAssignment(WebhooksMixin, ChangeLoggedModel):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    app_system = models.ForeignKey(
        to='netbox_app_systems.AppSystem',
        on_delete=models.PROTECT,
        related_name='appsystem_assignments'
    )

    clone_fields = ('content_type', 'object_id')

    class Meta:
        ordering = ['app_system']
        unique_together = ('content_type', 'object_id',
                           'app_system')

    def __str__(self):
        return str(self.app_system)

    def get_absolute_url(self):
        return reverse('plugins:netbox_app_systems:appsystem', args=[self.app_system.pk])
