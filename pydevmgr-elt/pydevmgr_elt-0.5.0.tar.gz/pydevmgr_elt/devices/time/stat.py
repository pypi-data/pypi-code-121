
from pydevmgr_core import  NodeAlias1, NodeAlias, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt, get_txt
from pydevmgr_ua import UaInterface
import datetime
from enum import Enum

Base = EltDevice.Interface # not the .Stat
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
class MODE(int, Enum):
    LOCAL                  =   0    
    UTC                    =   1
    SIMULATION             =   2
    
    UNREGISTERED = -9999

class STATUS(int, Enum):
    CONNECTED = 0
    NOT_CONNECTED = 1

class QOS(int, Enum):
    NOT_VALID = 0
    NOT_SYNCHRONIZED = 1
    VALID = 2





    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class TimeStat(Base):
    # Add the constants to this class 
    MODE = MODE
    QOS = QOS
    STATUS = STATUS
    fits_key = ""
    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        dc_time :  ND = NC(suffix="stat.sDcTime")
        utc_time : ND = NC(suffix="stat.sUtcTime")
        tai_time : ND = NC(suffix="stat.sTaiTime")
        error_msg : ND = NC(suffix="stat.sErrorMsg")
        mode :  ND = NC(suffix="stat.mode")
        ptp_offset_time : ND = NC(suffix="stat.lPtpOffsetTime")
        sim_offset_time : ND = NC(suffix="stat.lSimOffsetTime")
        dc_time_int : ND = NC(suffix="stat.lDcCurrentTime")
        utc_time_int : ND = NC(suffix="stat.lUtcTime")
        tai_time_int : ND = NC(suffix="stat.lTaiTime")
        tai_unix_time : ND = NC(suffix="stat.lTaiUnixTime")
        
    
        user_time : ND = NC(suffix="stat.sUserTime") 
        # STRING(29) := 'YYYY-MM-DD-hh:mm:ss.nnnnnnnnn';
        user_time_int :  ND = NC(suffix="stat.tUserTime") #      ULINT := 0;
        status: ND = NC(suffix="stat.signal.status")
        qos: ND = NC(suffix="stat.signal.qos")
        time_difference : ND = NC(suffix="stat.signal.time_difference") 
        #: UDINT; // Time difference between DC and External Time Source
    
    @NodeAlias.prop(nodes=["mode", "utc_time", "dc_time"])
    def time(self, mode: int, utc:str, dc:str) -> str:        
        """ Return a text representation of the mode """
        return dc if mode == self.MODE.LOCAL else utc 
    
    @NodeAlias1.prop(node="utc_time")
    def utc_datetime(self, utc):
        """ Convert the UTC returned by timer (which is not ISO) to a datetime 
        
        The returned datetime object is at nanosec precision 
        """
        return datetime.datetime.strptime( utc[:26] , '%Y-%m-%d-%H:%M:%S.%f')


    @NodeAlias1.prop(node="mode")
    def mode_txt(self, mode: int) -> str:
        """ Return a text representation of the mode """
        return get_txt(self.MODE(mode))
    
    @NodeAlias1.prop(node="qos")    
    def qos_txt(self, qos: int) -> str:
        """ Return a text representation of the qos """
        return get_txt( self.QOS(qos))
        
    @NodeAlias1.prop(node="status")
    def status_txt(self, status: int) -> str:
        """ Return a text representation of the status """
        return get_txt(self.QOS(status))



    
    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        dc_time : NV[str] = "" 
        utc_time : NV[str] = "" 
        tai_time : NV[str] = "" 
        error_msg : NV[str] = "" 
        mode :  NV[int] = 0
        mode_txt :  NV[str] = ""
        
        ptp_offset_time : NV[int] = 0 
        sim_offset_time : NV[int] = 0 
        dc_time_int     : NV[int] = 0 
        utc_time_int    : NV[int] = 0 
        tai_time_int    : NV[int] = 0 
        tai_unix_time   : NV[int] = 0 
        
        
        user_time : NV[str] = "" 
        user_time_int : NV[int] = 0 
        status :  NV[int] = 0 
        status_txt : NV[str] = ""
         
        qos: NV[int] = 0 
        qos_txt: NV[str] = 0 
        time_difference: NV[int] = 0


if __name__ == "__main__":
    TimeStat( )
