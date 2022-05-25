from pydantic import BaseModel
from pydevmgr_ua.config import UAConfig, uaconfig
from .io import IOConfig


class GROUP:
    """ Constants holder GROUP are used to classify state and substates
    
    This class is not intended to be instancied but only to hold constants
    
    An application if for widget styling for instance : one style per group
    
    """
    # for substate 
    IDL      = "IDL"
    WARNING  = "WARNING"
    ERROR    = "ERROR"
    OK       = "OK"
    NOK      = "NOK"
    BUZY     = "BUZY"
    UNKNOWN  = "UNKNOWN"
    
    # for modes 
    STATIC = "STATIC",
    TRACKING = "TRACKING", 
    ENG = "ENG"
    
    



class EltConfig(UAConfig):
    # default namespace 
    # namespace and host_mapping are inerited from UAConfig
    # input output configuration 
    io: IOConfig = IOConfig()

eltconfig = EltConfig.parse_obj(uaconfig)   
         
