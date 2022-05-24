# noqa: D100
from datetime import datetime
from typing import List

import pandas as pd

from bambooapi_client.openapi.apis import MarketsApi as _MarketsApi
from bambooapi_client.openapi.models import MarketPricesUnits


class MarketsApi(object):
    """Implementation for '/v1/sites' endpoints."""

    def __init__(self, bambooapi_client):
        self._bambooapi_client = bambooapi_client
        self._api_instance = _MarketsApi(bambooapi_client.api_client)

    def read_energy_market_prices(  # noqa: D102
        self,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
        units: str = MarketPricesUnits('MW').to_str(),
    ) -> pd.DataFrame:
        response = self._api_instance.read_energy_market_prices(
            market_id=market_id,
            start_time=start_time,
            end_time=end_time,
            units=units,
        )
        if response:
            return pd.DataFrame.from_records(
                [row.to_dict() for row in response],
                index='time',
            )
        else:
            return pd.DataFrame()

    def read_flexibility_market_prices(  # noqa: D102
        self,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
        units: str = MarketPricesUnits('MW').to_str(),
    ) -> pd.DataFrame:
        response = self._api_instance.read_flexibility_market_prices(
            market_id=market_id,
            start_time=start_time,
            end_time=end_time,
            units=units,
        )
        if response:
            return pd.DataFrame.from_records(
                [row.to_dict() for row in response],
                index='time',
            )
        else:
            return pd.DataFrame()

    def update_energy_market_prices(
        self,
        market_id: int,
        market_prices: pd.DataFrame,
    ) -> None:
        """Update energy market prices from a dataframe.

        Dataframe must be indexed by timezone-aware UTC-datetime,
        with index name `time` and with a column named `price`

        Example
        -------
        time,price
        2021-05-01 00:00:00+00:00,100.0
        2021-05-01 00:15:00+00:00,92.6
        2021-05-01 00:30:00+00:00,43.4

        Raises
        ------
        ValueError:
            If Dataframe has no columns or columns are not the expected ones.
        """
        self._validate_energy_market_prices(dataframe=market_prices)

        data_points = {
            'prices': market_prices.reset_index().to_dict(orient='records')
        }
        return self._api_instance.update_energy_market_prices(
            market_id=market_id,
            energy_market_prices_update=data_points,
        )

    def update_flexibility_market_prices(
        self,
        market_id: int,
        market_prices: pd.DataFrame,
    ) -> None:
        """Update flexibility market prices from a dataframe.

        Dataframe must have the following structure:
        * Indexed by timezone-aware UTC-datetime, with index name `time`
        * At least one of the columns `energy_price_up`, `energy_price_down` or
          `capacity_price` must exist.

        Example
        -------
        time,energy_prices_up,energy_prices_down,capacity_prices
        2021-05-01 00:00:00+00:00,100.0,70.0,23.0
        2021-05-01 00:15:00+00:00,92.6,42.6,35.3
        2021-05-01 00:30:00+00:00,43.4,13.4,26.5

        Raises
        ------
        ValueError:
            If Dataframe has no columns or columns are not the expected ones.
        """
        self._validate_flexibility_market_prices(dataframe=market_prices)

        expected_columns = self._flexibility_market_expected_columns()

        data_points = {}
        for column in market_prices.columns:
            if column not in expected_columns:
                continue
            df = market_prices[[column]]
            df = df.rename(columns={column: 'price'})
            data_points[column] = df.reset_index().to_dict(orient='records')

        self._api_instance.update_flexibility_market_prices(
            market_id=market_id,
            flexibility_market_prices_update=data_points,
        )

    @classmethod
    def _energy_market_expected_columns(cls) -> List[str]:
        return ['price']

    @classmethod
    def _flexibility_market_expected_columns(cls) -> List[str]:
        return ['energy_prices_up', 'energy_prices_down', 'capacity_prices']

    @classmethod
    def _validate_energy_market_prices(cls, dataframe: pd.DataFrame) -> None:
        expected_columns = cls._energy_market_expected_columns()
        if dataframe.columns != expected_columns:
            raise ValueError(
                f'Invalid columns. Expected columns {expected_columns}'
            )

    @classmethod
    def _validate_flexibility_market_prices(
        cls,
        dataframe: pd.DataFrame,
    ) -> None:
        expected_columns = cls._flexibility_market_expected_columns()
        if (
            len(dataframe.columns) == 0
            or not set(dataframe.columns).issubset(expected_columns)
        ):
            raise ValueError(
                f'Invalid columns. At least one of {expected_columns}'
            )
