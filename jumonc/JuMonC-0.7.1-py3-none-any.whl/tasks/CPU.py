import logging

from typing import Dict, List, Union, Optional
from types import ModuleType

from JuMonC.tasks import Plugin


logger = logging.getLogger(__name__)


class _CPUPlugin(Plugin.Plugin): 
    
    _psutil: Optional[ModuleType]
    
    def __init__(self) -> None:
        super().__init__()
        if self.isWorking():
            self.getLoad() # make sure it is correctly init even for windows
    
    
    def _isWorking(self) -> bool:
        try:
            self._psutil = __import__('psutil')
        except ModuleNotFoundError:
            logging.warning("psutil can not be imported, therefore CPU functionality not avaiable")
            return False
        return True
    
    def getLoad(self) -> List[float]:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.getloadavg()
        logging.error("Something went wrong, in cpu plugin psutil is not ModuleType")
        return [-1.0, -1.0, -1.0]
    
    
    def getStatusData(self,
                      dataType: str, 
                      overrideHumanReadableWithValue: Optional[bool] = None) -> List[Dict[str, Union[bool, int, float ,str]]]:
        logging.debug("get CPU status data with type=%s, overrride humand readable=%s",
                     str(dataType),
                     str(overrideHumanReadableWithValue))
        if dataType == "load":
            load = self.getLoad()
            return [{"load_1": load[0],
                     "load_5": load[1],
                     "load_15": load[2]}]
        return []
    
    
    def getConfigData(self,
                      dataType: str, 
                      overrideHumanReadableWithValue: Optional[bool] = None) -> List[Dict[str, Union[bool, int, float ,str]]]:
        logging.debug("get CPU config data with type=%s, overrride humand readable=%s",
                     str(dataType),
                     str(overrideHumanReadableWithValue))
        return []
    
    
plugin = _CPUPlugin()