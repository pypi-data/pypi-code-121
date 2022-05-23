import logging

from typing import Any, Dict, Optional

import threading



logger = logging.getLogger(__name__)


__data_lock: threading.Lock = threading.Lock()
__data: Dict[int, Optional[Any]] = {}

__id_lock: threading.Lock = threading.Lock()
__last_id: int = 0

def getNextDataID() -> int:
    global __last_id
    logging.debug("Waiting for next ID")
    with __id_lock:
        __last_id = __last_id + 1
        logging.debug("Next Id generated: %i", __last_id)
        return __last_id
    
def addResult(dataID: int, result: Optional[Any]) -> None:
    logging.debug("Waiting for access to data store")
    with __data_lock:
        __data[dataID] = result
        logging.debug("Data (%s) for ID %i stored", str(result), dataID)
    
def getResult(dataID: int) -> Optional[Any]:
    logging.debug("Waiting for access to data store")
    with __data_lock:
        result = __data[dataID]
        logging.debug("Data (%s) for ID %i retrived", str(result), dataID)
        return result
    
def removeResult(dataID: int) -> None:
    logging.debug("Waiting for access to data store")
    with __data_lock:
        del __data[dataID]
        logging.debug("Data for ID %i removed", dataID)