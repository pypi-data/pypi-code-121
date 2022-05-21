from dataclasses import dataclass
from pathlib import Path

from pkm.utils.monitors import MonitoredOperation, MonitoredEvent


@dataclass
class FetchResourceMonitoredOp(MonitoredOperation):
    resource_name: str
    resource_url: str


class FetchResourceCacheHitEvent(MonitoredEvent):
    ...


@dataclass
class FetchResourceDownloadStartEvent(MonitoredEvent):
    file_size: int
    store_path: Path
