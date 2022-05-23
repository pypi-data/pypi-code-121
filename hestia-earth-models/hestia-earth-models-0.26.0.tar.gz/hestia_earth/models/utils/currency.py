from dateutil.parser import parse
from currency_converter import CurrencyConverter

DEFAULT_CURRENCY = 'USD'
converter = CurrencyConverter(fallback_on_missing_rate=True,
                              fallback_on_missing_rate_method='last_known',
                              fallback_on_wrong_date=True)


def convert(amount: float, currency: str, date: str = None):
    try:
        return converter.convert(amount, currency, DEFAULT_CURRENCY, date=parse(date) if date else None)
    except ValueError:
        # handle "is not a supported currency" error
        return None
