from dataclasses import dataclass, field
from typing import List, Any, Optional

from bloc_client.value_type import ValueType
from bloc_client.select_options import SelectOption
from bloc_client.formcontrol_type import FormControlType


@dataclass
class IptComponent:
    value_type: ValueType
    formcontrol_type: FormControlType
    hint: str
    allow_multi: bool
    default_value: Optional[Any]=None
    select_options: List[SelectOption]=field(default_factory=list)
    value: Optional[Any]=None

    def json_dict(self):
        return {
            "value_type": self.value_type.value,
            "formcontrol_type": self.formcontrol_type.value,
            "hint": self.hint,
            "default_value": self.default_value,
            "allow_multi": self.allow_multi,
            "select_options": [i.json_dict() for i in self.select_options]
        }

@dataclass
class FunctionIpt:
    key: str
    display: str
    must: bool
    components: List[IptComponent]

    def json_dict(self):
        return {
            "key": self.key,
            "display": self.display,
            "must": self.must,
            "components": [i.json_dict() for i in self.components]
        }
