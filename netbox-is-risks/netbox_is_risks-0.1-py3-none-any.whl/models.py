from enum import unique
from django.contrib.postgres.fields import ArrayField
from django.db import models
from netbox.models import NetBoxModel, ChangeLoggedModel
from django.urls import reverse
from netbox.models.features import WebhooksMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Risk(NetBoxModel):
    name = models.CharField(
        max_length=250,
        unique=True
    )

    description = models.CharField(
        max_length=500,
        blank=True,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:risks:risk', args=[self.pk])


class RiskRelation(NetBoxModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.CharField(
        max_length=500,
        blank=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        # return 'reskrel'
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:risks:riskrelation', args=[self.pk])


class RiskAssignment(WebhooksMixin, ChangeLoggedModel):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    risk = models.ForeignKey(
        to='risks.Risk',
        on_delete=models.PROTECT,
        related_name='risk_assignments'
    )
    relation = models.ForeignKey(
        to='risks.RiskRelation',
        on_delete=models.PROTECT,
        related_name='risk_assignments'
    )

    clone_fields = ('content_type', 'object_id')

    class Meta:
        ordering = ['risk']
        unique_together = ('content_type', 'object_id',
                           'risk', 'relation')

    def __str__(self):
        return str(self.risk)

    def get_absolute_url(self):
        return reverse('plugins:risks:risk', args=[self.risk.pk])
