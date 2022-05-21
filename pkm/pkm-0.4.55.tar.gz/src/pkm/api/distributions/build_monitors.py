from dataclasses import dataclass

from pkm.api.packages.package import PackageDescriptor
from pkm.utils.monitors import MonitoredOperation, MonitoredEvent


@dataclass
class BuildPackageMonitoredOp(MonitoredOperation):
    package: PackageDescriptor
    distribution: str  # can be: wheel, metadata, editable_wheel, sdist


@dataclass
class BuildPackageHookExecutionEvent(MonitoredEvent):
    package: PackageDescriptor
    hook: str
