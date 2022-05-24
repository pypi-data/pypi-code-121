from .namespace import Namespace
from .container_namespace import ContainerNamespace
from .python_object_namespace import PythonObjectNamespace
from ...services.monitor.monitor_service import MonitorService

class ProcessStateNamespace(Namespace):
    def __init__(self):
        super(ProcessStateNamespace, self).__init__(self.METHODS)

    def dump(self, args):
        usage = MonitorService.get_last_usage()
        if not usage:
            return ContainerNamespace({})

        return ContainerNamespace(
            {
                "CPU": PythonObjectNamespace(usage.cpu),
                "GlobalCPU": PythonObjectNamespace(usage.global_cpu),
                "VirtualMemorySize": PythonObjectNamespace(usage.virtual_memory),
                "ProcessStartTime": PythonObjectNamespace(usage.start_time),
                "SystemUpTime": PythonObjectNamespace(usage.uptime),
            }
        )

    METHODS = (dump, )
