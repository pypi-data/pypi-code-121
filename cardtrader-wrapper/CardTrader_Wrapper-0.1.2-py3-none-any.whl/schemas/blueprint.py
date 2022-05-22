from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from dataclasses_json import Undefined, config, dataclass_json


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Property:
    name: str
    type_: str = field(metadata=config(field_name="type"))
    default_value: Optional[str] = None
    possible_values: List[Union[str, bool]] = field(default_factory=list)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Blueprint:
    category_id: int
    expansion_id: int
    game_id: int
    id_: int = field(metadata=config(field_name="id"))
    image_url: str
    name: str
    card_market_id: Optional[int] = None
    editable_properties: List[Property] = field(default_factory=list)
    fixed_properties: Dict[str, str] = field(default_factory=dict)
    scryfall_id: Optional[str] = None
    tcg_player_id: Optional[int] = None
    version: Optional[str] = None
