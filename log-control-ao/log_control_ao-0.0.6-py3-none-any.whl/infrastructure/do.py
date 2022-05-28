from typing import List, Optional
from dataclasses import dataclass
from ddd_objects.infrastructure.do import BaseDO

@dataclass
class LogRecordDO(BaseDO):
    log_type: str
    log_domain: str
    log_location: str
    log_inhalt: str
    log_label: Optional[List[str]]=None
    log_datetime: Optional[str]=None
    _life_time: Optional[int]=600