import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.attempt_statistics_data import AttemptStatisticsData
from ..models.statistics_period import StatisticsPeriod

T = TypeVar("T", bound="AttemptStatisticsResponse")


@attr.s(auto_attribs=True)
class AttemptStatisticsResponse:
    """
    Attributes:
        data (AttemptStatisticsData):
        end_date (datetime.datetime):
        period (StatisticsPeriod): Period length for a statistics data point
        start_date (datetime.datetime):
    """

    data: AttemptStatisticsData
    end_date: datetime.datetime
    period: StatisticsPeriod
    start_date: datetime.datetime
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.data.to_dict()

        end_date = self.end_date.isoformat()

        period = self.period.value

        start_date = self.start_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "endDate": end_date,
                "period": period,
                "startDate": start_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        data = AttemptStatisticsData.from_dict(dict_copy.pop("data"))

        end_date = isoparse(dict_copy.pop("endDate"))

        period = StatisticsPeriod(dict_copy.pop("period"))

        start_date = isoparse(dict_copy.pop("startDate"))

        attempt_statistics_response = cls(
            data=data,
            end_date=end_date,
            period=period,
            start_date=start_date,
        )

        attempt_statistics_response.additional_properties = dict_copy
        return attempt_statistics_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
