from enum import Enum
from types import SimpleNamespace


class Plan(Enum):
    """A Freshdesk plan."""

    BLOSSOM = dict(
        per_minute=100,
        ticket_create=40,
        ticket_update=40,
        ticket_list=40,
        contacts_list=40,
    )

    GARDEN = dict(
        per_minute=200,
        ticket_create=80,
        ticket_update=60,
        ticket_list=60,
        contacts_list=60,
    )

    ESTATE = dict(
        per_minute=400,
        ticket_create=160,
        ticket_update=160,
        ticket_list=100,
        contacts_list=100,
    )

    FOREST = dict(
        per_minute=700,
        ticket_create=280,
        ticket_update=280,
        ticket_list=200,
        contacts_list=200,
    )

    def __init__(self, value):

        self.rates = SimpleNamespace(**self.value)
