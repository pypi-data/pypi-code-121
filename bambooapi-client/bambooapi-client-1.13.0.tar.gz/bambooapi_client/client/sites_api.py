"""Sites are physical locations where flexibility devices are deployed."""
import typing as tp
from datetime import datetime

import pandas as pd

from bambooapi_client.openapi.apis import SitesApi as _SitesApi
from bambooapi_client.openapi.exceptions import NotFoundException
from bambooapi_client.openapi.models import (
    BaselineModel,
    DeviceActivation,
    FlexibilityModel,
    Horizon,
    PeriodRange,
    Site,
    SiteDataPoint,
    SiteListItem,
    ThermalZone,
    ThermalZoneSetpoints,
)


class SitesApi(object):
    """Implementation for '/v1/sites' endpoints."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = _SitesApi(bambooapi_client.api_client)

    def list_sites(self) -> tp.List[SiteListItem]:
        """List sites."""
        return self._api_instance.list_sites()

    def get_site(self, site_id: int) -> tp.Optional[Site]:
        """Get site by id."""
        try:
            return self._api_instance.read_site(site_id)
        except NotFoundException:
            return None

    def get_site_id(self, site_name: str) -> tp.Optional[int]:
        """Get site id by name."""
        try:
            return self._api_instance.get_site_id_by_name(site_name)
        except NotFoundException:
            return None

    def list_devices(
        self,
        site_id: int,
        device_type: str = 'thermal_loads',
    ) -> tp.List[tp.Any]:
        """List devices of a specified type for a given site."""
        return self._api_instance.list_devices(
            site_id,
            device_type=device_type,
        )

    def get_device(self, site_id: int, device_name: str) -> tp.Optional[dict]:
        """Get single device by name for a given site."""
        try:
            return self._api_instance.read_device(site_id, device_name)
        except NotFoundException:
            return None

    def list_thermal_zones(self, site_id: int) -> tp.List[ThermalZone]:
        """List zones for a given site."""
        return self._api_instance.list_thermal_zones(site_id)

    def get_thermal_zone(
        self,
        site_id: int,
        zone_name: str,
    ) -> tp.Optional[ThermalZone]:
        """Get single zone by name for a given site."""
        try:
            return self._api_instance.read_thermal_zone(site_id, zone_name)
        except NotFoundException:
            return None

    def read_device_baseline_model(
        self,
        site_id: int,
        device_name: str,
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> tp.Optional[BaselineModel]:
        """Read baseline model for a given site and device."""
        try:
            return self._api_instance.read_baseline_model(
                site_id,
                device_name,
                horizon=horizon,
            )
        except NotFoundException:
            return None

    def update_device_baseline_model(
        self,
        site_id: int,
        device_name: str,
        baseline_model: tp.Union[BaselineModel, dict],
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> BaselineModel:
        """Update baseline model for a given site and device."""
        return self._api_instance.update_baseline_model(
            site_id,
            device_name,
            baseline_model,
            horizon=horizon,
        )

    def read_device_measurements(
        self,
        site_id: int,
        device_name: str,
        start_time: datetime,
        end_time: datetime,
        frequency: tp.Optional[str] = None,
    ) -> tp.Optional[pd.DataFrame]:
        """Read site device measurements."""
        kwargs = dict(
            period=PeriodRange('CustomRange').to_str(),
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
        )
        if frequency:
            kwargs.update(frequency=frequency)
        _meas = self._api_instance.read_device_measurements(
            site_id,
            device_name,
            **kwargs,
        )
        # Convert SiteDataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_device_measurements(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
    ) -> None:
        """Update site device measurements."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        self._api_instance.insert_device_measurements(
            site_id,
            device_name,
            _dps,
        )

    def read_device_baseline_forecasts(
        self,
        site_id: int,
        device_name: str,
        start_time: datetime,
        end_time: datetime,
        horizon: str = Horizon('day-ahead').to_str(),
        frequency: tp.Optional[str] = None,
    ) -> pd.DataFrame:
        """Read site device forecasts."""
        kwargs = dict(
            horizon=horizon,
            period=PeriodRange('CustomRange').to_str(),
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
        )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_device_baseline_forecasts(
            site_id,
            device_name,
            **kwargs,
        )
        # Convert DataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_device_baseline_forecasts(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> tp.List[SiteDataPoint]:
        """Update site device baseline forecasts."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_baseline_forecasts(
            site_id,
            device_name,
            _dps,
            horizon=horizon,
        )

    def read_device_activations(
        self,
        site_id: int,
        device_name: str,
        end_time: tp.Optional[datetime] = None,
    ) -> tp.Optional[DeviceActivation]:
        """Read site device activations."""
        try:
            kwargs = {}
            if end_time:
                kwargs.update(end_time=end_time)
            return self._api_instance.read_device_activations(
                site_id,
                device_name,
                **kwargs,
            )
        except NotFoundException:
            return None

    def read_thermal_zone_flexibility_model(
        self,
        site_id: int,
        zone_name: str,
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> tp.Optional[FlexibilityModel]:
        """Read thermal flexibility model for a given site and zone."""
        try:
            return self._api_instance.read_flexibility_model(
                site_id,
                zone_name,
                horizon=horizon,
            )
        except NotFoundException:
            return None

    def update_thermal_zone_flexibility_model(
        self,
        site_id: int,
        zone_name: str,
        flexibility_model: tp.Union[FlexibilityModel, dict],
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> FlexibilityModel:
        """Update thermal flexibility model for a given site and zone."""
        return self._api_instance.update_flexibility_model(
            site_id,
            zone_name,
            flexibility_model,
            horizon=horizon,
        )

    def update_device_flexibility_forecast(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
        ramping: str,
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> tp.List[SiteDataPoint]:
        """Update device flexibility forecast."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_flexibility_forecasts(
            site_id=site_id,
            device_name=device_name,
            site_data_point=_dps,
            horizon=horizon,
            ramping=ramping,
        )

    def read_device_flexibility_forecast(
        self,
        site_id: int,
        device_name: str,
        ramping: str,
        start_time: datetime,
        end_time: datetime,
        horizon: str = Horizon('day-ahead').to_str(),
        frequency: tp.Optional[str] = None,
    ) -> pd.DataFrame:
        """Read site device flexibility."""
        kwargs = dict(
            period=PeriodRange('CustomRange').to_str(),
            start_time=start_time,
            end_time=end_time,
        )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_device_flexibility_forecasts(
            site_id=site_id,
            device_name=device_name,
            ramping=ramping,
            horizon=horizon,
            **kwargs,
        )
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_thermal_zone_flexibility_forecast(
        self,
        site_id: int,
        zone_name: str,
        data_frame: pd.DataFrame,
        ramping: str,
        horizon: str = Horizon('day-ahead').to_str(),
    ) -> tp.List[SiteDataPoint]:
        """Update site thermal zone flexibility forecast."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_thermal_zone_flexibility_forecasts(
            site_id=site_id,
            zone_name=zone_name,
            site_data_point=_dps,
            ramping=ramping,
            horizon=horizon,
        )

    def read_thermal_zone_flexibility_forecast(
        self,
        site_id: int,
        zone_name: str,
        ramping: str,
        start_time: tp.Optional[str] = None,
        end_time: tp.Optional[str] = None,
        horizon: str = Horizon('day-ahead').to_str(),
        frequency: tp.Optional[str] = None,
    ) -> pd.DataFrame:
        """Read site thermal zone flexibility forecast."""
        kwargs = dict(
            period=PeriodRange('CustomRange').to_str(),
            start_time=start_time,
            end_time=end_time,
        )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_thermal_zone_flexibility_forecasts(
            site_id=site_id,
            zone_name=zone_name,
            ramping=ramping,
            horizon=horizon,
            **kwargs,
        )
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def read_thermal_zone_setpoints(
        self,
        site_id: int,
        zone_name: str,
    ) -> ThermalZoneSetpoints:
        """Read site thermal zone setpoint."""
        return self._api_instance.read_thermal_zone_setpoints(
            site_id=site_id,
            zone_name=zone_name,
        )

    def update_thermal_zone_setpoints(
        self,
        site_id: int,
        zone_name: str,
        thermal_zone_setpoints: ThermalZoneSetpoints,
    ) -> ThermalZoneSetpoints:
        """Update site thermal zone setpoint."""
        return self._api_instance.update_thermal_zone_setpoints(
            site_id=site_id,
            zone_name=zone_name,
            thermal_zone_setpoints=thermal_zone_setpoints,
        )
