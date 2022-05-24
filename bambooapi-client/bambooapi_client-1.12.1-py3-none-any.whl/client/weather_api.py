"""Weather Stations are locations where weather data is pulled."""

import typing as tp

import pandas as pd

from bambooapi_client.openapi.apis import WeatherStationsApi
from bambooapi_client.openapi.exceptions import NotFoundException
from bambooapi_client.openapi.models import WeatherDataPoint, WeatherStation


class WeatherApi(object):
    """Implementation for '/v1/weather' endpoints."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = WeatherStationsApi(bambooapi_client.api_client)

    def list_weather_stations(self) -> tp.List[WeatherStation]:
        """List weather stations."""
        return self._api_instance.list_weather_stations()

    def get_weather_station(
        self,
        ws_id: int,
    ) -> tp.Optional[WeatherStation]:
        """Get weather station by ID."""
        try:
            return self._api_instance.read_weather_station(ws_id)
        except NotFoundException:
            return None

    def get_weather_station_id(self, ws_name: str) -> tp.Optional[int]:
        """Get weather station ID by name."""
        try:
            return self._api_instance.get_station_id_by_name(ws_name)
        except NotFoundException:
            return None

    def read_weather_forecasts(
        self,
        ws_id: int,
        start_time: tp.Optional[str] = None,
        end_time: tp.Optional[str] = None,
        frequency: tp.Optional[str] = None,
    ) -> tp.Optional[pd.DataFrame]:
        """Read weather forecasts."""
        kwargs = {}
        if start_time and end_time:
            kwargs.update(
                period='CustomRange',
                start_time=start_time,
                end_time=end_time,
            )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_weather_forecasts(ws_id, **kwargs)
        # Convert WeatherDataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_weather_forecasts(
        self,
        ws_id: int,
        data_frame: pd.DataFrame,
    ) -> tp.List[WeatherDataPoint]:
        """Update weather forecasts."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_weather_forecasts(ws_id, _dps)
