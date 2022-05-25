
from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

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



class SUBSTATE(int, Enum):
    NONE                  =   0    
    NOTOP_NOTREADY        = 100    
    NOTOP_INITIALISING    = 102    
    NOTOP_READY_OFF       = 103    
    NOTOP_READY_ON        = 104    
    NOTOP_ERROR           = 199    
    OP_DISABLING          = 205    
    OP_OFF                = 206    
    OP_SWITCHING_OFF      = 207    
    OP_COOLING            = 208    
    OP_ON                 = 209    
    OP_SWITCHING_ON       = 210    
    OP_WARMING            = 211    
    OP_ERROR              = 299
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute         
enum_group ({
        SUBSTATE.NONE                   : GROUP.UNKNOWN,
        SUBSTATE.NOTOP_NOTREADY         : GROUP.NOK,
        SUBSTATE.NOTOP_READY_OFF        : GROUP.NOK,
        SUBSTATE.NOTOP_READY_ON         : GROUP.NOK,
        SUBSTATE.NOTOP_INITIALISING     : GROUP.BUZY,
        SUBSTATE.NOTOP_ERROR            : GROUP.ERROR, 
  
        SUBSTATE.OP_DISABLING            : GROUP.BUZY, 
        SUBSTATE.OP_SWITCHING_OFF        : GROUP.BUZY,
        SUBSTATE.OP_SWITCHING_ON         : GROUP.BUZY,

        SUBSTATE.OP_COOLING              : GROUP.BUZY,
        SUBSTATE.OP_WARMING              : GROUP.BUZY,
        SUBSTATE.OP_ON                   : GROUP.OK,
        SUBSTATE.OP_OFF                  : GROUP.OK,
        SUBSTATE.OP_ERROR                : GROUP.ERROR,    
    })
    


class ERROR(int,  Enum):
    OK				      = _inc(0) # init the inc to zero 
    HW_NOT_OP           = _inc()
    INIT_FAILURE        = _inc()		
    UNEXPECTED_OFF      = _inc()
    UNEXPECTED_ON       = _inc()
    FAULT_SIG           = _inc()
    MAXON               = _inc()
    STILL_COOLING       = _inc()
    TIMEOUT_DISABLE     = _inc()
    TIMEOUT_INIT        = _inc()
    TIMEOUT_OFF         = _inc()
    TIMEOUT_ON          = _inc()
    # Simulator errors
    SIM_NOT_INITIALISED	= 90
    SIM_NULL_POINTER    = 100	

    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute     
enum_txt ({
    ERROR.OK:				   'OK',
	ERROR.HW_NOT_OP:			 'ERROR: TwinCAT not in OP state or CouplerState not mapped.',
    ERROR.INIT_FAILURE:		     'ERROR: INIT command aborted due to STOP or RESET.',
	ERROR.UNEXPECTED_OFF:		 'ERROR: Lamp unexpectedly switched OFF.',
	ERROR.UNEXPECTED_ON:		 'ERROR: Lamp unexpectedly switched ON.',
	ERROR.FAULT_SIG:			 'ERROR: Fault signal active.',
	ERROR.MAXON:				 'ERROR: Lamp maximum ON time exceeded.',
	ERROR.STILL_COOLING:		 'ERROR: ON command not allowed while cooling.',
	ERROR.TIMEOUT_DISABLE:	     'ERROR: Disable timed out.',
	ERROR.TIMEOUT_INIT:		     'ERROR: Init timed out.',
	ERROR.TIMEOUT_OFF:		     'ERROR: Switching OFF timed out.',
	ERROR.TIMEOUT_ON:			 'ERROR: Switching ON timed out.',
	ERROR.SIM_NOT_INITIALISED:   'ERROR: Lamp simulator not initialised.',
	ERROR.SIM_NULL_POINTER:	     'ERROR: NULL pointer to Lamp.',

    ERROR.UNREGISTERED:        'ERROR: Unregistered Error'
    })



    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class LampStat(Base):
    # Add the constants to this class 
    ERROR = ERROR
    SUBSTATE = SUBSTATE
    
    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        check_time_left: ND = NC(suffix='stat.bCheckTimeLeft' )
        error_code: ND = NC(suffix='stat.nErrorCode' )
        intensity: ND = NC(suffix='stat.lrIntensity' )
        local: ND = NC(suffix='stat.bLocal' )
        state: ND = NC(suffix='stat.nState' )
        status: ND = NC(suffix='stat.nStatus' )
        substate: ND = NC(suffix='stat.nSubstate' )
        time_left: ND = NC(suffix='stat.nTimeLeft' )
    
    @NodeAlias1.prop(node="substate")
    def is_ready(self, substate):
        """ Alias node: True if lamp is ready (substate NOTOP_READY_ON or NOTOP_READY_OFF) """
        return substate in [self.SUBSTATE.NOTOP_READY_ON, self.SUBSTATE.NOTOP_READY_OFF]
    
    @NodeAlias1.prop(node="substate")
    def is_off(self, substate):
        """  Alias node: True if lamp is off """
        return substate == self.SUBSTATE.OP_OFF
    
    @NodeAlias1.prop(node="substate")
    def is_on(self, substate):
        """  Alias node: True if lamp is on """
        return substate == self.SUBSTATE.OP_ON



    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        check_time_left: NV[bool] = False
        error_code: NV[int] = 0
        intensity: NV[float] = 0.0
        local: NV[bool] = False
        state: NV[int] = 0
        status: NV[int] = 0
        substate: NV[int] = 0
        time_left: NV[int] = 0


if __name__ == "__main__":
    LampStat( local=NC(parser=float) )
