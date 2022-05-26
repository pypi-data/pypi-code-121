import random

from httpx import AsyncClient as Client

from faker import Faker
from pytest import mark as _mark


mark_async = _mark.asyncio

locales = ('ru_RU', 'en_US')

Faker.seed(random.randint(0, 99999))
faker: Faker = Faker(locale=locales)


def shake_faker():
    """Shake faker seed."""
    Faker.seed(random.randint(0, 100))


def country_name() -> str:
    """Gen country name."""
    shake_faker()
    return str(faker.country())


def currency_name() -> str:
    """Gen currency name."""
    shake_faker()
    return str(faker.currency_name())


def currency_code() -> str:
    """Gen currency code."""
    shake_faker()
    return str(faker.currency_code())


def money_amount(min_amount: float = 0, max_amount: float = 99999.99) -> float:
    """Gen money amount."""
    return round(random.uniform(min_amount, max_amount), ndigits=2)


def any_word() -> str:
    """Any word."""
    shake_faker()
    return faker.word()


def any_sentence() -> str:
    """Any sentence."""
    shake_faker()
    return faker.sentence()


def any_bool() -> bool:
    """Any bool."""
    return random.choice([True, False])


def any_url() -> str:
    """Any url."""
    shake_faker()
    return faker.url()


def any_image_url() -> str:
    """Any image url."""
    shake_faker()
    return faker.image_url()


__all__ = (
    'Client', 'mark_async', 'faker', 'locales',

    'country_name',
    'currency_name',
    'currency_code',
    'money_amount',
    'any_word',
    'any_sentence',
    'any_bool',
    'any_url',
    'any_image_url',
)
