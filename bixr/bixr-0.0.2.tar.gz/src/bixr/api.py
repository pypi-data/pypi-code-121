from decimal import Decimal
import datetime

from .llapi import LLAPI

try:
    # Required only when calling API methods
    import pandas as pd
except ImportError:
    pd = None


def check_pandas(func):
    def wrapper(*args, **kwargs):
        assert pd is not None
        return func(*args, **kwargs)

    return wrapper


class API(LLAPI):
    @check_pandas
    def daily_range_df(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        base_currency: str,
        quote_currency: str,
        invert_quote_base: bool = True,
    ):
        resp_json = self.daily_range(
            start_date, end_date, base_currency, quote_currency, lang="en"
        )
        return rates2df(
            resp_json["rates"],
            base_currency,
            quote_currency,
            resp_json["resultsInfo"]["exchangeConventionCode"],
            invert_quote_base,
            "%Y-%m-%d",
        )

    def monthly_range_df(
        self,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        base_currency: str,
        quote_currency: str,
        invert_quote_base: bool = True,
    ):
        resp_json = self.monthly_range(
            start_year,
            start_month,
            end_year,
            end_month,
            base_currency,
            quote_currency,
            lang="en",
        )
        return rates2df(
            resp_json["rates"],
            base_currency,
            quote_currency,
            resp_json["resultsInfo"]["exchangeConventionCode"],
            invert_quote_base,
            "%Y-%m",
        )

    def yearly_range_df(
        self,
        start_year: int,
        end_year: int,
        base_currency: str,
        quote_currency: str,
        invert_quote_base: bool = True,
    ):
        resp_json = self.yearly_range(
            start_year,
            end_year,
            base_currency,
            quote_currency,
            lang="en",
        )
        return rates2df(
            resp_json["rates"],
            base_currency,
            quote_currency,
            resp_json["resultsInfo"]["exchangeConventionCode"],
            invert_quote_base,
            "%Y",
        )


def rates2df(
    rates,
    base_currency,
    quote_currency,
    exchange_convention_code,
    invert_quote_base,
    date_format,
):
    df = pd.DataFrame(rates)
    assert (df.columns == ["referenceDate", "avgRate", "exchangeConvention"]).all()

    df["baseCurrency"] = base_currency
    df["quoteCurrency"] = quote_currency
    df["baseCurrency"] = df["baseCurrency"].astype("category")
    df["quoteCurrency"] = df["quoteCurrency"].astype("category")

    # Use exchange convention code instead of description
    df.drop(columns=["exchangeConvention"], inplace=True)
    df["exchangeConventionCode"] = exchange_convention_code
    df["exchangeConventionCode"] = df["exchangeConventionCode"].astype("category")

    # Timezone is always Europe/Rome
    df["referenceDate"] = pd.to_datetime(
        df["referenceDate"], format=date_format
    ).dt.tz_localize("Europe/Rome")

    df["avgRate"] = df["avgRate"].apply(Decimal)

    # Invert rate if not base/quote
    if invert_quote_base and exchange_convention_code == "I":
        df["avgRate"] = 1 / df["avgRate"]
        df["exchangeConventionCode"] = "C"

    df.set_index("referenceDate", verify_integrity=True, inplace=True)
    df.sort_index(inplace=True)

    return df
