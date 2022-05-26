import dataclasses
from typing import List


@dataclasses.dataclass
class ScaleResponse:
    requested_instances: int
    created_instances_ips: List[str]
