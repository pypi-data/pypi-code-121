import dataclasses
import typing


@dataclasses.dataclass
class JustNimbusModel:
    pump_flow: int
    drink_flow: int
    pump_pressure: int
    pump_starts: int
    pump_hours: int
    reservoir_temp: int
    reservoir_content: int
    total_saved: int
    total_replenished: int
    error_code: int
    totver: int
    reservoir_content_max: int

    @classmethod
    def from_dict(cls, data: typing.Dict):
        return JustNimbusModel(**{
            key.name: data.get(key.name)
            for key in dataclasses.fields(JustNimbusModel)
        })
