"""
Pydantic models for custom Promethee periods
"""
import abc
from typing import Any, List, Tuple, Union, Optional

from pydantic import BaseModel, Field, validator, root_validator

from mfire.settings import get_logger
from mfire.utils.date import Datetime, Timedelta
import mfire.composite as composite

LOGGER = get_logger(name=__name__, bind="periods")


class PeriodElementConfig(BaseModel):
    """ Cette classe permet de créer un objet PeriodElementConfig

    Inheritance : BaseModel

    Returns:
        baseModel : objet PeriodElementConfig
    """

    start: Optional[int] = Field(None)
    delta_start: Optional[int] = Field(None, alias="deltaStart")
    absolu_start: Optional[Datetime] = Field(None, alias="absoluStart")
    stop: Optional[int] = Field(None)
    delta_stop: Optional[int] = Field(None, alias="deltaStop")
    absolu_stop: Optional[Datetime] = Field(None, alias="absoluStop")
    production_time_until: int = Field(24, ge=0, le=24, alias="productionTime_until")

    @root_validator(pre=True)
    def init_start_stop(cls, values: dict) -> dict:
        """validator to check the given period element consistency
        """
        # check start
        start_keys = ("start", "deltaStart", "absoluStart")
        start_count = sum(key in values for key in start_keys)
        if start_count != 1:
            raise ValueError(f"Exactly one 'start' key expected. {start_count} given.")

        if "absoluStart" in values:
            values["absoluStart"] = Datetime(values["absoluStart"])

        # check stop
        stop_keys = ("stop", "deltaStop", "absoluStop")
        stop_count = sum(key in values for key in stop_keys)
        if stop_count != 1:
            raise ValueError(f"Exactly one 'stop' key expected. {stop_count} given.")

        if "absoluStop" in values:
            values["absoluStop"] = Datetime(values["absoluStop"])

        return values

    def get_bound_datetime(
        self, reference_datetime: Datetime, bound_name: str
    ) -> Datetime:
        """Method creating a datetime out of a given bound_name and
        a reference datetime.
        Example:
        >>> el = PeriodElement(deltaStart=1, stop=32, productionTime_until=16)
        >>> ref_dt = Datetime(2021, 11, 3, 10)
        >>> el.get_bound_datetime(ref_dt, "start")
        Datetime(2021, 11, 3, 11)
        >>> el.get_bound_datetime(ref_dt, "stop")
        Datetime(2021, 11, 4, 8)
        >>> el.get_bound_datetime(Datetime(2021, 11, 3, 17), "stop")
        Datetime(2021, 11, 5, 8)

        >>> el = PeriodElement(
        >>>    start=1, absoluStop=Datetime(2021, 1, 1), productionTime_until=16
        >>> )
        >>> el.get_bound_datetime(ref_dt, "stop")
        Datetime(2021, 1, 1)

        Args:
            reference_datetime (Datetime): Reference datetime.
            bound_key (str): Key representing the bound (e.g. "start", "delta_start",
                "absolu_start", etc.)
            bound (Union[int, Datetime]): Value to transform as datetime.
            next_day (bool, optional): Whether we must look forward to the day after the
                given reference one. Only used when bound_key is "start" or "stop".
                    Defaults to False.

        Returns:
            Datetime: datetime corresponding to the given bound and reference datetime.
        """
        bound_key, bound_value = next(
            (
                (key, val)
                for key, val in self.dict().items()
                if bound_name in key and val is not None
            ),
            (bound_name, None),
        )
        if bound_value is None:
            LOGGER.error(
                f"(bound_key, bound_value)=({bound_key}, {bound_value}) "
                f"with bound_name={bound_name}",
                **self.dict(),
            )

        if bound_key.startswith("absolu"):
            result = bound_value

        elif bound_key.startswith("delta"):
            result = reference_datetime + Timedelta(hours=bound_value)

        else:
            nb_days = int(reference_datetime.hour > self.production_time_until)
            result = reference_datetime.midnight + Timedelta(
                days=nb_days, hours=bound_value
            )

        if result < reference_datetime:
            LOGGER.warning(
                f"Configured '{bound_name}' datetime ({result}) is before the given "
                f"reference datetime ({reference_datetime})."
            )
        return result

    def get_start_stop_datetime(
        self, reference_datetime: Datetime
    ) -> Tuple[Datetime, Datetime]:
        """Returns the start and stop datetime corresponding to
        the self configuration and a given reference datetime.

        Args:
            reference_datetime (Datetime): Reference datetime

        Returns:
            Tuple[Datetime, Datetime]: Start and stop datetime.
        """
        start = self.get_bound_datetime(reference_datetime, "start")
        stop = self.get_bound_datetime(reference_datetime, "stop")

        if start > stop:
            LOGGER.warning(
                f"Configured start datetime ({start}) is after the "
                f"configured stop datetime ({stop})."
            )
        return start, stop


class _AbstractPeriodConfig(BaseModel, abc.ABC):
    """Abstract Period class with an id, a name and an abstract method
    get_processed_period"""

    id: str
    name: Optional[str] = None

    @abc.abstractmethod
    def get_processed_period(self, production_datetime: Datetime) -> composite.Period:
        """Returns the processed period (mfire.composite.periods.Period) corresponding
        to the given production datetime.

        Args:
            production_datetime (Datetime): Current production datetime.

        Returns:
            composite.Period: Period with concrete start and stop datetimes.
        """
        pass


class PeriodSingleElementConfig(_AbstractPeriodConfig, PeriodElementConfig):
    """PeriodSingleElement class : Period without a list of periodElements"""

    def get_processed_period(self, production_datetime: Datetime) -> composite.Period:
        start, stop = self.get_start_stop_datetime(production_datetime)
        return composite.Period(id=self.id, name=self.name, start=start, stop=stop)


class PeriodMultipleElementConfig(_AbstractPeriodConfig):
    """PeriodMultipleElement: class Period with multiple periodElements"""

    period_elements: List[PeriodElementConfig] = Field(
        ..., min_items=1, alias="periodElements"
    )

    @validator("period_elements")
    def sort_elements(
        cls, elements: List[PeriodElementConfig]
    ) -> List[PeriodElementConfig]:
        """validator sorting given period elements
        """
        return sorted(elements, key=lambda element: element.production_time_until)

    def get_processed_period(self, production_datetime: Datetime) -> composite.Period:
        element = next(
            (
                el
                for el in self.period_elements
                if production_datetime.hour < el.production_time_until
            ),
            self.period_elements[0],
        )
        start, stop = element.get_start_stop_datetime(production_datetime)
        return composite.Period(id=self.id, name=self.name, start=start, stop=stop)


PeriodConfig = Union[PeriodSingleElementConfig, PeriodMultipleElementConfig]


class PeriodCollectionConfig(BaseModel):
    """ Cette classe permet de créer un objet PeriodCollectionConfig

    Inheritance : BaseModel

    Returns:
        baseModel : liste d'objet PeriodConfig
    """

    periods: List[PeriodConfig]

    def __iter__(self):
        """iterate over periods"""
        return iter(self.periods)

    def __len__(self):
        """return periods length"""
        return len(self.periods)

    def __getitem__(self, id: str) -> PeriodConfig:
        """get periods at a given index"""
        try:
            return next(period for period in self.periods if period.id == id)
        except StopIteration:
            raise KeyError(f"'{id}'")

    def get(self, index: str, default: Any = None) -> PeriodConfig:
        """get period with a default value in case
        """
        try:
            return self[index]
        except KeyError:
            return default

    def get_processed_periods(
        self, production_datetime: Datetime
    ) -> composite.PeriodCollection:
        return composite.PeriodCollection(
            periods=[
                period.get_processed_period(production_datetime)
                for period in self.periods
            ]
        )


def period_factory(configuration: dict) -> PeriodConfig:
    """Factory function for creating the proper PeriodConfig object
    according to the given configuration.

    Args:
        configuration (dict): Configuration dictionary.

    Returns:
        Period: Corresponding period.
    """
    if "periodElements" in configuration:
        return PeriodMultipleElementConfig(**configuration)
    else:
        return PeriodSingleElementConfig(**configuration)
