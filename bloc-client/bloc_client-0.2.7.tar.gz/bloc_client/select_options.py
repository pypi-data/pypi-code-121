from typing import Any
from dataclasses import dataclass


@dataclass
class SelectOption:
    label: str
    value: Any

    def json_dict(self):
        return {
            'label': self.label,
            'value': self.value
        }
