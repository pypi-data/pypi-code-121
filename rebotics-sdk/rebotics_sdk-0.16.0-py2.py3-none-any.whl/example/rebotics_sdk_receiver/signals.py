from django.dispatch import receiver

from rebotics_sdk.hook.signals import (
    IMPORT_FINISH,
    PROCESSING_FINISH,
    IMPORT_FINISH_ERROR,
    IMPORT_FINISH_SUCCESS,
    PROCESSING_FINISH_ERROR,
    PROCESSING_FINISH_SUCCESS,
)


@receiver(IMPORT_FINISH)
def handle_message(sender, retailer, event, payload, **kwargs):
    print('sender: {}'.format(sender))
    print('{} {} {}'.format(retailer, event, payload))


@receiver(PROCESSING_FINISH)
def handle_message(sender, retailer, event, payload, **kwargs):
    print('sender: {}'.format(sender))
    print('{} {} {}'.format(retailer, event, payload))


@receiver(IMPORT_FINISH_ERROR)
def handle_message(sender, retailer, event, payload, **kwargs):
    print('sender: {}'.format(sender))
    print('{} {} {}'.format(retailer, event, payload))


@receiver(IMPORT_FINISH_SUCCESS)
def handle_message(sender, retailer, event, payload, **kwargs):
    print('sender: {}'.format(sender))
    print('{} {} {}'.format(retailer, event, payload))


@receiver(PROCESSING_FINISH_ERROR)
def handle_message(sender, retailer, event, payload, **kwargs):
    print('sender: {}'.format(sender))
    print('{} {} {}'.format(retailer, event, payload))


@receiver(PROCESSING_FINISH_SUCCESS)
def handle_message(sender, retailer, event, payload, **kwargs):
    print('sender: {}'.format(sender))
    print('{} {} {}'.format(retailer, event, payload))

