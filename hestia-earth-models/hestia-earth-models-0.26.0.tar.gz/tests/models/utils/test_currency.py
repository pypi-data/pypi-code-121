from hestia_earth.models.utils.currency import convert


def test_convert_eur():
    amount = 10
    currency = 'EUR'
    assert convert(amount, currency, '2000') > 0


def test_convert_usd():
    amount = 10
    currency = 'USD'
    assert convert(amount, currency) == amount
