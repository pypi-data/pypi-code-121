from django_omise.models.event import EventType, Event
from django_omise.models.core import Charge
from django_omise.omise import omise

from django_omise.utils.core_utils import update_or_create_from_omise_object


from typing import Dict


def pre_event_handle(omise_event: omise.Event, raw_event: Dict):
    """
    Perform additional actions on Omise Event object before handling with the webhook view.

    :params omise_event: The Omise Event object
    :param raw_event: The event data as received with webhook view

    :returns: None
    """
    if omise_event.key == EventType.REFUND_CREATE.value:
        charge = Charge.objects.get(pk=omise_event.data.charge)
        charge.reload_from_omise()

    if omise_event.key.startswith("schedule."):
        update_or_create_from_omise_object(
            omise_object=omise_event.data,
            ignore_fields=[
                "occurrences",
            ],
        )


def post_event_handle(omise_event: omise.Event, event_object: Event, raw_event: Dict):
    """
    Perform additional actions on Omise Event object after handling with the webhook view.

    :params omise_event: The Omise Event object
    :param event_object: The new event object in the database
    :param raw_event: The event data as received with webhook view

    :returns: None
    """

    if omise_event.key.startswith("charge."):

        schedule_id = raw_event.get("data", {}).get("schedule", None)
        omise_schedule = None
        schedule = None

        if schedule_id:
            omise_schedule = omise.Schedule.retrieve(schedule_id)
            schedule = update_or_create_from_omise_object(omise_object=omise_schedule)

        charge = event_object.event_object
        charge.schedule = schedule
        charge.save()

    if omise_event.key.startswith("customer."):

        customer = event_object.event_object
        for schedule in customer.schedules:
            schedule.reload_from_omise()
