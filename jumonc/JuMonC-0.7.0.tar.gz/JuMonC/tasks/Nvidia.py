import logging

from typing import Optional, Dict, Any, List
from types import ModuleType

from JuMonC.tasks import Plugin


logger = logging.getLogger(__name__)

class _NvidiaPlugin(Plugin.Plugin):
    
    _pynvml: Optional[ModuleType]
    _smi: Optional[ModuleType]
    
    _config = ["driver_version", "count", "name", "serial", "vbios_version",
              "display_mode", "persistence_mode", "compute_mode",
              "pci.bus_id", "pci.bus", "pcie.link.gen.max", "pcie.link.width.max",
              "clocks_throttle_reasons.supported", "clocks.max.graphics", "clocks.max.sm", "clocks.max.memory"
              "power.management", "power.limit", "power.min_limit", "power.max_limit",]
    _status = ["pcie.link.gen.current", "pcie.link.width.current",
              "fan.speed", "power.draw", "pstate",
              "memory.total", "memory.used", "memory.free",
              "utilization.gpu", "utilization.memory",
              "temperature.gpu", "temperature.memory",
              "clocks.current.graphic", "clocks.current.sm", "clocks.current.memory", "clocks.current.video",
              "clocks.applications.graphics", "clocks.applications.memory",
              "mig.mode.current", "mig.mode.pending"]
    
    def __init__(self) -> None:
        """Init pynvml!"""
        super().__init__()
        if self.isWorking():
            if isinstance(self._pynvml, ModuleType):
                try:
                    self._pynvml.nvmlInit()
                except self._pynvml.nvml.NVMLError_LibraryNotFound:
                    logging.warning("pynvml cannot find needed gpu libraries, therefore gpu functionality not avaiable")
                    self.works = False
                    return
                    
            if isinstance(self._smi, ModuleType):
                self.nvsmi = self._smi.smi.nvidia_smi.getInstance()
            else:
                logging.error("Something went wrong, in gpu plugin, pynvml is not ModuleType")

    
    def _isWorking(self) -> bool:
        try:
            self._pynvml = __import__('pynvml')
        except ModuleNotFoundError:
            logging.warning("pynvml can not be imported, therefore gpu functionality not avaiable")
            return False
        try:
            self._smi = __import__('pynvml.smi')
        except ModuleNotFoundError:
            logging.warning("pynvml.smi can not be imported, therefore gpu functionality not avaiable")
            return False
        return True
    
    def _getInfo(self, name:str) -> Dict[str, Any]:
        return self.nvsmi.DeviceQuery(name)
    
    def getConfigList(self) -> List[str]:
        return self._config
    
    def getStatusList(self) -> List[str]:
        return self._status
    
    def getConfigData(self, dataType:str) -> Dict[str, Any]:
        if dataType in self._config:
            return self._getInfo(dataType)
        return {}
    
    def getStatusData(self, dataType:str) -> Dict[str, Any]:
        if dataType in self._status:
            return self._getInfo(dataType)
        return {}
    
    
plugin = _NvidiaPlugin()