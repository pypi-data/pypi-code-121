
from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt, get_txt

from enum import Enum
Base = EltDevice.Interface

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 
#                      _              _   
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ 
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __|
# | (_| (_) | | | \__ \ || (_| | | | | |_ 
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|
# 

##### ###########
# SUBSTATE
class TIME_MODE(int, Enum):
    LOCAL                  =   0    
    UTC                    =   1
    
    UNREGISTERED = -9999


    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class CcsSimStat(Base):
    # Add the constants to this class 
    TIME_MODE = TIME_MODE

    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        time_mode  : ND = NC(suffix="stat.nTimeMode")
        sdc_time   : ND = NC(suffix="stat.sDcTime")
        dc_time    : ND = NC(suffix="stat.lDcTime")
        apparent_alpha: ND = NC(suffix="stat.apparent.alpha")
        apparent_delta: ND = NC(suffix="stat.apparent.delta")
        alpha : ND = NC(suffix="stat.observed.alpha")
        delta : ND = NC(suffix="stat.observed.delta")
        ha : ND = NC(suffix="stat.observed.ha")
        zd : ND = NC(suffix="stat.observed.zd")
        az : ND = NC(suffix="stat.observed.az")
        temperature: ND = NC(suffix="stat.environment.temperature ")
        pressure: ND = NC(suffix="stat.environment.pressure ")
        humidity: ND = NC(suffix="stat.environment.humidity")
        lapserate: ND = NC(suffix="stat.environment.lapserate")
        lst : ND = NC(suffix="stat.data.lst")
        pa  : ND = NC(suffix="stat.data.pa")
        pa_deg : ND = NC(suffix="stat.data.pa_deg")
        alt : ND = NC(suffix="stat.data.alt")
        alt_deg : ND = NC(suffix="stat.data.alt_deg")
        ha: ND = NC(suffix="stat.data.ha")
        az: ND = NC(suffix="stat.data.az")
        az_deg : ND = NC(suffix="stat.data.az_deg")
        rotation: ND = NC(suffix="stat.data.rotation")
        rotation_deg : ND = NC(suffix="stat.data.rotation_deg")
        ra: ND = NC(suffix="stat.data.ra")
        dec: ND = NC(suffix="stat.data.dec")

    @NodeAlias1.prop(node="time_mode")
    def time_mode_txt(self, time_mode: int) -> str:
        """ Return a text representation of the time_mode """
        return get_txt( self.TIME_MODE(time_mode) )
    


    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        time_mode: NV[int] = 0
        sdc_time: NV[str]  = ""
        dc_time : NV[int] = 0  
        
        apparent_alpha: NV[float] = 0.0 
        apparent_delta: NV[float] = 0.0 
        alpha :  NV[float]  = 0.0 
        delta :  NV[float]  = 0.0 
        ha :  NV[float]  = 0.0  
        zd :  NV[float]  = 0.0  
        az :  NV[float]  = 0.0 
         
        
        temperature: NV[float]  = 0.0  
        pressure: NV[float]     = 0.0     
        humidity: NV[float]     = 0.0     
        lapserate: NV[float]    = 0.0    
        
        lst : NV[float] = 0.0
        pa  : NV[float] = 0.0
        pa_deg : NV[float] = 0.0
        alt : NV[float] = 0.0
        alt_deg : NV[float] = 0.0
        ha: NV[float] = 0.0
        az: NV[float] = 0.0
        az_deg : NV[float] = 0.0
        rotation: NV[float] = 0.0
        rotation_deg : NV[float] = 0.0
        ra: NV[float] = 0.0
        dec: NV[float] = 0.0


if __name__ == "__main__":
    CcsSimStat( )
