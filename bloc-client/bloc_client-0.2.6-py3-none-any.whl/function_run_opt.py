from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class FunctionRunOpt:
    suc: bool=True
    canceled: bool=False
    timeout_canceled: bool=False
    intercept_below_function_run: bool=False
    error_msg: str=""
    description: str=""
    optKey_map_data: Optional[Dict[str, Any]]=None
    optKey_map_objectStorageKey: Optional[Dict[str, str]]=None
    optKey_map_briefData: Optional[Dict[str, str]]=None

    @property
    def finished_report_dict(self):
        return {
            "suc": self.suc,
            "canceled": self.canceled,
            "timeout_canceled": self.timeout_canceled,
            "intercept_below_function_run": self.intercept_below_function_run,
            "error_msg": self.error_msg,
            "description": self.description,
            "optKey_map_briefData": self.optKey_map_briefData,
            "optKey_map_objectStorageKey": self.optKey_map_objectStorageKey}
