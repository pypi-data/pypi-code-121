import logging

from typing import Dict, List, Union, Optional
from types import ModuleType

from JuMonC.tasks import Plugin
from JuMonC.helpers import convertNumbers
from JuMonC import settings


logger = logging.getLogger(__name__)


class _diskPlugin(Plugin.Plugin): 
    
    _psutil: Optional[ModuleType]
    
    def __init__(self) -> None:
        super().__init__()
        if self.isWorking():
            if isinstance(self._psutil, ModuleType):
                self._initValues = self._psutil.disk_io_counters()
            else:
                logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
            
    
    
    def _isWorking(self) -> bool:
        try:
            self._psutil = __import__('psutil')
        except ModuleNotFoundError:
            logging.warning("psutil can not be imported, therefore disk functionality not avaiable")
            return False
        return True
    
    def getReadCount(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().read_count - self._initValues.read_count
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getWriteCount(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().write_count - self._initValues.write_count
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getReadBytes(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().read_bytes - self._initValues.read_bytes
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getWriteBytes(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().write_bytes - self._initValues.write_bytes
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getReadTime(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().read_time - self._initValues.read_time
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getWriteTime(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().write_time - self._initValues.write_time
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getReadMergedCount(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().read_merged_count - self._initValues.read_merged_count
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getWriteMergedCount(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().write_merged_count - self._initValues.write_merged_count
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getBusyTime(self) -> int:
        if isinstance(self._psutil, ModuleType):
            return self._psutil.disk_io_counters().busy_time - self._initValues.busy_time
        logging.error("Something went wrong, in disk plugin psutil is not ModuleType")
        return -1
    
    def getStatusData(self,
                      dataType: str, 
                      duration: float = -1.0, 
                      overrideHumanReadableWithValue: Optional[bool] = None) -> List[Dict[str, Union[bool, int, float ,str]]]:
        logging.debug("get disk status data with type=%s, duration=%s, overrride humand readable=%s",
                     str(dataType),
                     str(duration),
                     str(overrideHumanReadableWithValue))
        if dataType == "write_count":
            return [self.convertNumber(self.getWriteCount(), "write count", "", overrideHumanReadableWithValue)]
        if dataType == "read_count":
            return [self.convertNumber(self.getReadCount(), "read count", "", overrideHumanReadableWithValue)]
        if dataType == "write_bytes":
            return [self.convertNumber(self.getWriteBytes(), "write", "B", overrideHumanReadableWithValue)]
        if dataType == "read_bytes":
            return [self.convertNumber(self.getReadBytes(), "read", "B", overrideHumanReadableWithValue)]
        if dataType == "write_time":
            return [self.convertNumber(self.getWriteTime()/1000, "write", "s", overrideHumanReadableWithValue)]
        if dataType == "read_time":
            return [self.convertNumber(self.getReadTime()/1000, "read", "s", overrideHumanReadableWithValue)]
        if dataType == "write_merged_count":
            return [self.convertNumber(self.getWriteMergedCount(), "merged write", "", overrideHumanReadableWithValue)]
        if dataType == "read_merged_count":
            return [self.convertNumber(self.getReadMergedCount(), "merged read", "", overrideHumanReadableWithValue)]
        if dataType == "busy_time":
            return [self.convertNumber(self.getBusyTime()/1000, "busy", "s", overrideHumanReadableWithValue)]
        return []
    
    
    def getConfigData(self,
                      dataType: str, 
                      overrideHumanReadableWithValue: Optional[bool] = None) -> List[Dict[str, Union[bool, int, float ,str]]]:
        logging.debug("get disk config data with type=%s, overrride humand readable=%s",
                     str(dataType),
                     str(overrideHumanReadableWithValue))
        return []
    
    
    def convertNumber(self, 
                      num: Union[int,float], 
                      name: str, 
                      unit: str, 
                      overrideHumanReadableWithValue: Optional[bool]
                ) -> Dict[str, Union[bool, int, float ,str]]:
        if overrideHumanReadableWithValue or (overrideHumanReadableWithValue is None and settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS) :
            (value, unitPrefix) = convertNumbers.convertBinaryPrefix(num)
            return {name + "[" + unitPrefix + unit + "]" : value}
        
        return {name + "[" + unit + "]" : str(num)}
    
    
plugin = _diskPlugin()
