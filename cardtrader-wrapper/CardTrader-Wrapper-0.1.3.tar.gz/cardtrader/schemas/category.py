from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import Undefined, config, dataclass_json


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Property:
    name: str
    type_: str = field(metadata=config(field_name="type"))
    possible_values: List[Union[str, bool]] = field(default_factory=list)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Category:
    game_id: int
    id_: int = field(metadata=config(field_name="id"))
    name: str
    properties: List[Property] = field(default_factory=list)
