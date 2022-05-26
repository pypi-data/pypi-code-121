import re
from functools import cached_property
from typing import Dict, List, Optional

from policy_sentry.querying.arns import get_matching_raw_arns


class RawARN:
    _all_defaults = {}

    @classmethod
    def with_shared_defaults(cls, template: str):
        return cls(template, cls._all_defaults)

    @classmethod
    def validate(cls, arn: str):
        try:
            return bool(get_matching_raw_arns(arn))
        except:
            return False

    def __init__(self, template: str, defaults: Optional[Dict[str, str]] = None) -> None:
        self.template = template
        self._defaults = defaults or {}

    @cached_property
    def fields(self) -> List[str]:
        return re.findall(r"\$\{(\w+)\}", self.template)

    @property
    def defaults(self) -> Dict[str, str]:
        return {"Partition": "aws", **self._defaults}

    def set(self, field: str, value: str):
        self._defaults[field] = value

    def update(self, values: Dict[str, str]):
        self._defaults.update(values)

    def values(self) -> Dict[str, str]:
        return {field: self.defaults.get(field, "") for field in self.fields}

    def format(self):
        return self.template.replace("$", "").format(**self.values())

    def __str__(self):
        return self.format()
