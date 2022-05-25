
from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt
from pydevmgr_elt.devices.motor import Motor

from enum import Enum
Base = EltDevice.Stat

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

##### ############
# SUBSTATE
class SUBSTATE(int, Enum):
    NONE =  0

    NOTOP_NOTREADY =  100
    NOTOP_READY = 101
    NOTOP_INITIALIZING = 102
    NOTOP_ABORTING = 107
    NOTOP_RESETTING = 109
    NOTOP_ENABLING = 110
    
    NOTOP_ERROR =  199

    OP_DISABLING 	= 205
    OP_STANDSTILL	= 216
    OP_MOVING		= 217
    OP_SETTING_POS	= 218
    OP_STOPPING		= 219
    OP_TRACKING		= 220
    OP_PRESETTING	= 221

    OP_ERROR =299
    
    UNREGISTERED = -9999
    
enum_group({
    SUBSTATE.NOTOP_NOTREADY     :  GROUP.NOK, 
    SUBSTATE.NOTOP_READY        :  GROUP.NOK,
    SUBSTATE.NOTOP_INITIALIZING :  GROUP.BUZY, 
    SUBSTATE.NOTOP_ABORTING     :  GROUP.BUZY, 
    SUBSTATE.NOTOP_RESETTING    :  GROUP.BUZY, 
    SUBSTATE.NOTOP_ENABLING     :  GROUP.BUZY, 
    SUBSTATE.NOTOP_ERROR        :  GROUP.ERROR, 
    SUBSTATE.OP_DISABLING 	    :  GROUP.BUZY, 
    SUBSTATE.OP_STANDSTILL	    :  GROUP.OK,
    SUBSTATE.OP_MOVING		    :  GROUP.BUZY, 
    SUBSTATE.OP_SETTING_POS	    :  GROUP.BUZY, 
    SUBSTATE.OP_STOPPING		:  GROUP.BUZY, 
    SUBSTATE.OP_TRACKING		:  GROUP.OK, 
    SUBSTATE.OP_PRESETTING	    :  GROUP.BUZY, 
    SUBSTATE.OP_ERROR           :  GROUP.ERROR,   
    })



ERROR = Motor.Stat.ERROR

class AXIS(int, Enum):
    """ AXIS enumeration has defined inside the PLC """
    ALL_AXIS = 0
    AXIS1 = 1
    AXIS2 = 2

### ############# 
# Mode 
class MODE(int, Enum):
    """ The three ADC modes """
    ENG   = 0 
    OFF   = 1
    AUTO  = 2

enum_group({ # associate mode to group (used for graphical representation)
    MODE.ENG    : GROUP.ENG,
    MODE.OFF	: GROUP.STATIC,
    MODE.AUTO	: GROUP.TRACKING,
})




    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class AdcStat(Base):
    # Add the constants to this class 
    ERROR = ERROR
    SUBSTATE = SUBSTATE
    MODE = MODE 
    AXIS = AXIS
    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        state:             ND = NC(suffix="stat.sm.nState")
        substate:          ND = NC(suffix="stat.sm.nSubstate")
        initialised:       ND = NC(suffix="stat.bInitialised")
        track_mode:        ND = NC(suffix="stat.nMode")
        alpha:             ND = NC(suffix="stat.apparent.alpha")
        delta:             ND = NC(suffix="stat.apparent.delta")
        error_code:        ND = NC(suffix="stat.nErrorCode")
        status:            ND = NC(suffix="stat.nStatus")
        local:             ND = NC(suffix="stat.bLocal")
        
  

    @NodeAlias1.prop(node="track_mode")
    def track_mode_txt(self, track_mode: int) -> str:
        return self.MODE(track_mode).name
    
    @NodeAlias1.prop(node="substate")
    def is_presetting(self,  substate: int) -> bool:
        """ -> True is axis is preseting """
        return substate == self.SUBSTATE.OP_PRESETTING
    
    @NodeAlias1.prop(node="substate")
    def is_tracking(self,  substate: int) -> bool:
        """ -> True is axis is tracking """
        return substate == self.SUBSTATE.OP_TRACKING

    @NodeAlias1.prop(node="substate")
    def is_moving(self, substate: int) -> bool:
        """ -> True is axis is moving """
        return substate == self.SUBSTATE.OP_MOVING

    @NodeAlias1.prop(node="substate")
    def is_standstill(self,  substate: int) -> bool:
        """ -> True is axis is standstill """
        return substate == self.SUBSTATE.OP_STANDSTILL

    
    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        error_code: NV[ERROR] = ERROR.OK
        initialised:     NV[bool] =   False
        track_mode:      NV[int] =    0  
        alpha:           NV[float] =  0.0 
        delta:           NV[float] =  0.0 
        error_code:      NV[int] =    0  
        status:          NV[int] =    0  
        local:           NV[bool] =   False  

        track_mode: NV[int] = 0  
        is_moving: NV[bool] = False
        is_standstill : NV[bool] = False 
        is_presetting : NV[bool] = False
        is_tracking: NV[bool] = False 
        pass

if __name__ == "__main__":
    AdcStat( )
