from .base import OmiseBaseModel

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

from django_omise.omise import omise

from enum import Enum


class EventType(Enum):
    """
    All Omise event types.

    See each type description here https://www.omise.co/api-webhooks.
    """

    CARD_DESTROY = "card.destroy"
    CARD_UPDATE = "card.update"

    CHARGE_CAPTURE = "charge.capture"
    CHARGE_COMPLETE = "charge.complete"
    CHARGE_CREATE = "charge.create"
    CHARGE_EXPIRE = "charge.expire"
    CHARGE_REVERSE = "charge.reverse"
    CHARGE_UPDATE = "charge.update"

    CUSTOMER_CREATE = "customer.create"
    CUSTOMER_DESTROY = "customer.destroy"
    CUSTOMER_UPDATE = "customer.update"
    CUSTOMER_UPDATE_CARD = "customer.update.card"

    DISPUTE_ACCEPT = "dispute.accept"
    DISPUTE_CLOSE = "dispute.close"
    DISPUTE_CREATE = "dispute.create"
    DISPUTE_UPDATE = "dispute.update"

    LINK_CREATE = "link.create"

    RECIPIENT_ACTIVATE = "recipient.activate"
    RECIPIENT_CREATE = "recipient.create"
    RECIPIENT_DEACTIVATE = "recipient.deactivate"
    RECIPIENT_DESTROY = "recipient.destroy"
    RECIPIENT_UPDATE = "recipient.update"
    RECIPIENT_VERIFY = "recipient.verify"

    REFUND_CREATE = "refund.create"

    SCHEDULE_CREATE = "schedule.create"
    SCHEDULE_DESTROY = "schedule.destroy"
    SCHEDULE_EXPIRE = "schedule.expire"
    SCHEDULE_EXPIRING = "schedule.expiring"
    SCHEDULE_SUSPEND = "schedule.suspend"

    TRANSFER_CREATE = "transfer.create"
    TRANSFER_DESTROY = "transfer.destroy"
    TRANSFER_FAIL = "transfer.fail"
    TRANSFER_PAY = "transfer.pay"
    TRANSFER_SEND = "transfer.send"
    TRANSFER_UPDATE = "transfer.update"


class Event(OmiseBaseModel):

    omise_class = omise.Event

    event_type_choices = [(event.value, event.name) for event in EventType]

    event_type = models.CharField(max_length=50, choices=event_type_choices)

    data = models.JSONField(default=dict)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.CharField(max_length=255, blank=True, null=True)
    event_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
