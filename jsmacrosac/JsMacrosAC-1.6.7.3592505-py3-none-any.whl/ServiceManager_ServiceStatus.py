from typing import overload
from typing import List


class ServiceManager_ServiceStatus:
	ENABLED: "ServiceManager_ServiceStatus"
	DISABLED: "ServiceManager_ServiceStatus"
	RUNNING: "ServiceManager_ServiceStatus"
	STOPPED: "ServiceManager_ServiceStatus"
	UNKNOWN: "ServiceManager_ServiceStatus"

	@overload
	def values(self) -> List["ServiceManager_ServiceStatus"]:
		pass

	@overload
	def valueOf(self, name: str) -> "ServiceManager_ServiceStatus":
		pass

	pass


