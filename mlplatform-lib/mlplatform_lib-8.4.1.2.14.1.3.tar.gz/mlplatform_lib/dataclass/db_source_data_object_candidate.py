from typing import Optional
from dataclasses import dataclass


@dataclass
class DbSourceDataObjectCandidate:
    name: str
    resource_type: str
    comments: Optional[str]
