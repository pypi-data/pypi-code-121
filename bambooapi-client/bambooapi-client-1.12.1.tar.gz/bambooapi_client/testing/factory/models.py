"""Factory classes to generate random instances of API models."""
from datetime import timedelta

from bambooapi_client.openapi import exceptions
from bambooapi_client.openapi.models import (
    AlgorithmEnum,
    BaselineModel,
    Battery,
    CurtailableLoad,
    Devices,
    EVCharger,
    FlexibilityModel,
    Frequency,
    KernelBaselineModel,
    KNNBaselineModel,
    KNNWeightsEnum,
    Load,
    Meter,
    Microgrid,
    PVSystem,
    RCModel,
    TariffCreate,
    TariffSpecsCreate,
    SetpointTemp,
    ShiftableLoad,
    Site,
    SiteDataPoint,
    ThermalComfortDevice,
    ThermalLoad,
    ThermalZone,
    ThermalZoneSetpoints,
    WeatherDataPoint,
    WeatherStation,
    ZoneThermalComfortDevice,
    ZoneThermalLoad,
)

from . import faker


class FactoryMetaClass(type):
    """Factory metaclass."""

    def __call__(cls, **kwargs):
        """Override the default Factory() syntax to call cls.create method.

        Returns an instance of the associated class.
        """
        return cls.create(**kwargs)


class Factory(metaclass=FactoryMetaClass):  # noqa: D101
    model = None
    default_kwargs = {}

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of type cls.model.

        cls.model constructor is called with cls.default_kwargs, which will be
        overwritten by **kwargs (if provided).

        cls.default_kwargs must be a dictionary with literal values or callable
        objects.

        Examples of cls.default_kwargs with literal values.

        Examples
        --------
        >>> class ComplexFactory(Factory):
        ...     model=complex
        ...     default_kwargs={'real': 1, 'imag': 2}
        ...
        >>> ComplexFactory()
        (1+2j)
        >>> ComplexFactory(imag=42)
        (1+42j)

        Additionally, cls.default_kwargs values can be callable objects. This
        is handy to produce different outcomes at each call.

        Examples
        --------
        >>> from bambooapi_client.testing.factory.faker import incremental_id
        >>> class ComplexRandomFactory(Factory):
        ...     model=complex
        ...     default_kwargs={
        ...         'real': incremental_id(start=42),
        ...         'imag': 2,
        ...     }
        ...
        >>> ComplexRandomFactory()
        (42+2j)
        >>> ComplexRandomFactory()
        (43+2j)

        Raises
        ------
        NotImplementedError
            If cls.model is not set
            If cls.default_kwargs is not an instance of a dict
        exceptions.ApiTypeError
            If instance is being instanciated with invalid or missing
            arguments.
        """
        if not hasattr(cls, 'model') or cls.model is None:
            raise NotImplementedError('class attributes not specified')
        if not isinstance(cls.default_kwargs, dict):
            raise NotImplementedError('class default arguments not specified')

        _kwargs = {**cls.default_kwargs, **kwargs}
        if hasattr(cls.model, 'attribute_map'):
            actual_keys = set(_kwargs.keys())
            expected_keys = set(cls.model.attribute_map.keys())
            if expected_keys != actual_keys:
                msg = (
                    f'Invalid arguments provided to {cls}. Expected arguments '
                    f'{sorted(expected_keys)}. Got arguments '
                    f'{sorted(actual_keys)}'
                )
                raise exceptions.ApiTypeError(msg)
        evaluated_kwargs = {
            key: kwarg() if callable(kwarg) else kwarg
            for key, kwarg in _kwargs.items()
        }
        return cls.model(**evaluated_kwargs)


class MeterFactory(Factory):  # noqa: D101
    model = Meter
    default_kwargs = dict(
        name=faker.random_string(),
        max_power=faker.random_float(100, 150),
        # Todo: min_power is negative on energy consumption. Update backend.
        min_power=0.,
        units='kW',
        controllable='',
    )


class LoadFactory(Factory):  # noqa: D101
    model = Load
    default_kwargs = dict(
        name='load',
        max_power=faker.random_float(100, 150),
        min_power=0.,
        units='kW',
        controllable='',
    )


class CurtailableLoadFactory(Factory):  # noqa: D101
    model = CurtailableLoad
    default_kwargs = dict(
        name=faker.random_string(),
        max_power=faker.random_float(100, 150),
        min_power=0.,
        units='kW',
        type='lighting_system',
        controllable='luxsp',
        max_control=faker.random_int(100, 150),
    )


class ShiftableLoadFactory(Factory):  # noqa: D101
    model = ShiftableLoad
    default_kwargs = dict(
        name=faker.random_string(),
        max_power=faker.random_float(100, 150),
        min_power=0.,
        units='kW',
        type='production_line',
        maximum_energetic_debt=faker.random_float(500.0, 1200.0),
        controllable='',
    )


class PVSystemFactory(Factory):  # noqa: D101
    model = PVSystem
    default_kwargs = dict(
        name=faker.random_string(),
        peak_power=faker.random_float(25.0, 50.0),
        nominal_power=faker.random_float(25.0, 50.0),
        min_power=0.0,
        tilt=faker.random_int(20, 60),
        azimuth=faker.random_int(90, 270),
        losses=faker.random_int(10, 30),
        units='kW',
        self_consumption=True,
        controllable='',
    )


class EVChargerFactory(Factory):  # noqa: D101
    model = EVCharger
    default_kwargs = dict(
        name=faker.random_string(),
        max_power=faker.random_float(5, 30),
        min_power=0.,
        units='kW',
        self_consumption=True,
        controllable='',
    )


class BatteryFactory(Factory):  # noqa: D101
    model = Battery
    default_kwargs = dict(
        name=faker.random_string(),
        units='kW',
        max_soc=faker.random_int(80, 95),
        min_soc=faker.random_int(10, 20),
        charge_max_power=faker.random_float(5, 30),
        discharge_max_power=faker.random_float(5, 30),
        charge_efficiency=faker.random_float(0.8, 0.95),
        discharge_efficiency=faker.random_float(0.8, 0.95),
        capacity=faker.random_int(10, 25),
        self_consumption=True,
        controllable='',
    )


class ThermalLoadFactory(Factory):  # noqa: D101
    model = ThermalLoad
    default_kwargs = dict(
        name=faker.random_string(),
        max_power=faker.random_float(20, 50),
        min_power=0.,
        units='kW',
        cop=faker.random_float(2.5, 4.5),
        virtual_device=faker.random_choice([True, False]),
        associated_meter=faker.random_string(),
        controllable='',
    )


class ThermalComfortDeviceFactory(Factory):  # noqa: D101
    model = ThermalComfortDevice
    default_kwargs = dict(
        name=faker.random_string(),
        units='ºC',
        controllable='',
    )


class ZoneThermalLoadFactory(Factory):  # noqa: D101
    model = ZoneThermalLoad
    default_kwargs = dict(
        name=faker.random_string(),
        influence=1.0,
    )


class ZoneThermalComfortDeviceFactory(Factory):  # noqa: D101
    model = ZoneThermalComfortDevice
    default_kwargs = dict(
        name=faker.random_string(),
    )


class ThermalZoneFactory(Factory):  # noqa: D101
    model = ThermalZone
    default_kwargs = dict(
        name=faker.random_string(),
        thermal_loads=faker.list_(ZoneThermalLoadFactory, 1),
        thermal_comfort_devices=faker.list_(
            ZoneThermalComfortDeviceFactory,
            1,
        ),
        adjacent=list,
        controllable='',
    )


class DevicesFactory(Factory):  # noqa: D101
    model = Devices
    default_kwargs = dict(
        meters=faker.list_(MeterFactory, 1),
        loads=faker.list_(LoadFactory, 1),
        curtailable_loads=faker.list_(CurtailableLoadFactory, 1),
        shiftable_loads=faker.list_(ShiftableLoadFactory, 1),
        pv_systems=faker.list_(PVSystemFactory, 1),
        ev_chargers=faker.list_(EVChargerFactory, 1),
        batteries=faker.list_(BatteryFactory, 1),
        thermal_loads=faker.list_(ThermalLoadFactory, 1),
        thermal_comfort_devices=faker.list_(ThermalComfortDeviceFactory, 1),
    )


class MicrogridFactory(Factory):  # noqa: D101
    model = Microgrid
    default_kwargs = dict(
        devices=DevicesFactory,
        thermal_zones=faker.list_(ThermalZoneFactory, 1),
    )


class SiteFactory(Factory):  # noqa: D101
    model = Site
    default_kwargs = dict(
        site_name=faker.random_string(),
        display_name=faker.random_string(),
        site_id=faker.incremental_id(),
        flexumer_id=faker.incremental_id(),
        weather_id=faker.incremental_id(),
        microgrid=MicrogridFactory,
        energy_injection=True,
        location=faker.random_country(),
        country=faker.random_country(),
        country_code=faker.random_country_code(),
        timezone='Europe/Madrid',
        latitude=faker.random_float(-50.0, 50.0),
        longitude=faker.random_float(-50.0, 50.0),
        elevation=faker.random_float(0.0, 1000),
    )


class SiteDataPointFactory(Factory):  # noqa: D101
    model = SiteDataPoint
    default_kwargs = dict(
        mode=faker.random_choice(['cold', 'heat']),
        time=faker.incremental_datetime(),
        soc=faker.random_float(0, 100),
        power=faker.random_float(0.0, 5.0),
        powersp=faker.random_float(-10.0, 10.0),
        temp=faker.random_float(25.0, 30.0),
        humidity=faker.random_float(20, 100),
        tempsp=faker.random_float(18.0, 26.0),
        vref=faker.random_int(0, 100),
        schedule=False,
        availability=True,
        status=True,
        quality=True,
    )


class WeatherDataPointFactory(Factory):  # noqa: D101
    model = WeatherDataPoint
    default_kwargs = dict(
        dewpoint=faker.random_float(-50.0, 50.0),
        humidity=faker.random_float(.0, 100.0),
        irradiance=faker.random_float(2.3, 4.5),
        pressure=faker.random_float(40000, 80000),
        temperature=faker.random_float(-20, 40),
        windspeed=faker.random_float(.0, 100.0),
        quality=True,
        time=faker.incremental_datetime(),
    )


class WeatherStationFactory(Factory):  # noqa: D101
    model = WeatherStation
    default_kwargs = dict(
        station_name=faker.random_string(length=8),
        station_id=faker.incremental_id(),
        latitude=faker.random_float(-50.0, 50.0),
        longitude=faker.random_float(-50.0, 50.0),
        elevation=faker.random_float(0.0, 1000),
    )


class TariffCreateFactory(Factory):  # noqa: D101
    model = TariffCreate
    default_kwargs = dict(
        tariff_name=faker.random_string(length=5),
        display_name=faker.random_string(length=5),
        country_code='ES-B',
    )


class TariffSpecsCreateFactory(Factory):  # noqa: D101
    model = TariffSpecsCreate
    default_kwargs = dict(
        energy_fees=faker.tariff_specs_energy_fees(['P1', 'P2', 'P3']),
        periods=faker.tariff_specs_periods(
            keys=[
                'january',
                'february',
                'march',
                'april',
                'may',
                'june',
                'july',
                'august',
                'september',
                'october',
                'november',
                'december',
                'weekend_holiday',
            ],
            periods_names=['P1', 'P2', 'P3'],
        ),
        start_time=faker.incremental_datetime(increment=timedelta(days=1)),
        end_time=faker.incremental_datetime(increment=timedelta(days=1)),
    )


class RCModelFactory(Factory):  # noqa: D101
    model = RCModel
    default_kwargs = dict(
        c=faker.random_float(-100000, 100000),
        r1=faker.random_float(0.0, 10000),
        r2=faker.random_float(0.0, 10000),
        r3=faker.random_float(0.0, 10000),
        r4=faker.random_float(0.0, 10000),
        window_area=faker.random_float(0.0, 1000),
        internal_gains=faker.random_float(0.0, 1000),
        rmse=faker.random_float(0.0, 1000),
        trained_param=faker.random_choice((0, 1,)),
        last_update=faker.incremental_datetime(
            increment=timedelta(days=1),
        ),
    )


class SetpointTempFactory(Factory):  # noqa: D101
    model = SetpointTemp
    default_kwargs = dict(
        temp_set=faker.random_float(0.0, 100.0),
        temp_min=faker.random_float(0.0, 100.0),
        temp_max=faker.random_float(0.0, 100.0),
    )


class FlexibilityModelFactory(Factory):  # noqa: D101
    model = FlexibilityModel
    default_kwargs = dict(
        rc_model=RCModelFactory,
    )


class ThermalZoneSetpointsFactory(Factory):  # noqa: D101
    model = ThermalZoneSetpoints
    default_kwargs = dict(
        mode=faker.random_choice(
            tuple(ThermalZoneSetpoints.allowed_values[('mode',)].values())
        ),
        heating_setpoint=SetpointTempFactory,
        cooling_setpoint=SetpointTempFactory,
    )


class KernelBaselineModelFactory(Factory):  # noqa: D101
    model = KernelBaselineModel
    default_kwargs = dict(
        bandwidths=faker.list_(faker.random_float(0.0, 1.0), length=7)
    )


class KNNBaselineModelFactory(Factory):  # noqa: D101
    model = KNNBaselineModel
    default_kwargs = dict(
        number_neighbours=faker.random_int(3, 6),
        weights=KNNWeightsEnum('uniform'),
    )


class BaselineModelFactory(Factory):  # noqa: D101
    model = BaselineModel
    default_kwargs = dict(
        algorithm=faker.random_algorithm(),
        frequency=faker.random_frequency(),
        interpolation_threshold=faker.random_int(0, 60),
        last_update=faker.incremental_datetime(),
        model=KernelBaselineModelFactory().to_dict(),
        training_set={},
    )
