from dataclasses import dataclass

from pkm.api.packages.package import PackageDescriptor
from pkm.utils.monitors import MonitoredOperation


@dataclass
class PackageInstallMonitoredOp(MonitoredOperation):
    package: PackageDescriptor
