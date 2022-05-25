
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
    OFF = 0
    NOT_OP = 1
    OP = 2
    NOT_OP_NOT_READY = 100
    NOT_OP_INITIALIZING = 102
    NOT_OP_READY_CLOSED = 105
    NOT_OP_READY_OPEN = 106
    NOT_OP_FAILURE = 199
    NOT_OP_ERROR = 199
    OP_DISABLING = 205
    OP_CLOSED = 212
    OP_CLOSING = 213
    OP_OPEN = 214
    OP_OPENING = 215
    OP_FAILURE = 299
    
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute         
enum_group ({
        SUBSTATE.OFF                   : GROUP.UNKNOWN,
        SUBSTATE.OP                    : GROUP.OK,
        SUBSTATE.NOT_OP_NOT_READY      : GROUP.NOK,
        SUBSTATE.NOT_OP_READY_CLOSED   : GROUP.NOK,
        SUBSTATE.NOT_OP_READY_OPEN     : GROUP.NOK,
        SUBSTATE.NOT_OP_INITIALIZING   : GROUP.BUZY,
        SUBSTATE.NOT_OP_FAILURE        : GROUP.ERROR,
        SUBSTATE.OP_DISABLING          : GROUP.BUZY, 
        SUBSTATE.OP_CLOSING            : GROUP.BUZY, 
        SUBSTATE.OP_OPENING            : GROUP.BUZY,
        SUBSTATE.OP_FAILURE            : GROUP.ERROR,
        SUBSTATE.OP_CLOSED             : GROUP.OK, 
        SUBSTATE.OP_OPEN               : GROUP.OK,    
    })
    


class ERROR(int,  Enum):
    OK				      = _inc(0) # init the inc to zero 
    HW_NOT_OP             = _inc()	# increment number  		
    INIT_FAILURE          = _inc()	
    UNEXPECTED_CLOSED     = _inc()	
    UNEXPECTED_NONE       = _inc()	
    UNEXPECTED_OPENED     = _inc()	
    FAULT_SIG             = _inc()	
    BOTH_SIG_ACTIVE       = _inc()
    TIMEOUT_ENABLE        = _inc()
    TIMEOUT_DISABLE       = _inc()
    TIMEOUT_INIT          = _inc()
    TIMEOUT_CLOSE         = _inc()
    TIMEOUT_OPEN          = _inc()
    
    SIM_NOT_INITIALISED		= 90
    SIM_NULL_POINTER		= 100	# Simulator error
    
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute     
enum_txt ({
    ERROR.OK:				   'OK',
    ERROR.HW_NOT_OP:		   'ERROR: TwinCAT not in OP state or CouplerState not mapped.',
    ERROR.INIT_FAILURE:	       'ERROR: INIT command aborted due to STOP or RESET.',
    ERROR.UNEXPECTED_CLOSED:   'ERROR: Shutter unexpectedly closed.',
    ERROR.UNEXPECTED_NONE:     'ERROR: Unexpectedly no OPEN or CLOSED signal active.',
    ERROR.UNEXPECTED_OPENED:   'ERROR: Shutter unexpectedly opened.',
    ERROR.FAULT_SIG:		   'ERROR: Fault signal active.',
    ERROR.BOTH_SIG_ACTIVE:     'ERROR: Both OPEN and CLOSED signals active.',
    ERROR.TIMEOUT_ENABLE:	   'ERROR: ENABLE timed out.',
    ERROR.TIMEOUT_DISABLE:     'ERROR: DISABLE timed out.',
    ERROR.TIMEOUT_INIT:	       'ERROR: INIT timed out.',
    ERROR.TIMEOUT_CLOSE:	   'ERROR: CLOSE timed out.',
    ERROR.TIMEOUT_OPEN:		   'ERROR: OPEN timed out.',
    ERROR.SIM_NOT_INITIALISED: 'ERROR: Shutter simulator not initialised.',
        ERROR.SIM_NULL_POINTER:	   'ERROR: NULL pointer to Shutter.',
        
        ERROR.UNREGISTERED:        'ERROR: Unregistered Error'
    })



    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class ShutterStat(Base):
    # Add the constants to this class 
    ERROR = ERROR
    SUBSTATE = SUBSTATE
    
    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        error_code: ND = NC(suffix='stat.nErrorCode' )
        local: Defaults[NC] = NC(suffix='stat.bLocal' )
        state: ND = NC(suffix='stat.nState' )
        status: ND = NC(suffix='stat.nStatus' )
        substate: ND = NC(suffix='stat.nSubstate' )


    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    @NodeAlias1.prop("is_ready", "substate")
    def is_ready(self, substate):
        """ True if device is ready """
        return substate in [self.SUBSTATE.NOT_OP_READY_OPEN, self.SUBSTATE.NOT_OP_READY_CLOSED]
    
    @NodeAlias1.prop("is_not_ready", "substate")
    def is_not_ready(self, substate):
        """ True if device is not ready """
        return substate in [self.SUBSTATE.NOT_OP_NOT_READY]
    
    @NodeAlias1.prop("is_open", "substate")
    def is_open(self, substate):
        """ True if shutter is OPEN  """
        return substate in [self.SUBSTATE.OP_OPEN, self.SUBSTATE.NOT_OP_READY_OPEN]
    
    @NodeAlias1.prop(node="substate")
    def is_closed(self, substate):
        return substate in [self.SUBSTATE.OP_CLOSED, self.SUBSTATE.NOT_OP_READY_CLOSED]
        
    @NodeAlias1.prop("is_in_error", "substate")
    def is_in_error(self, substate: int) -> bool:
        """ -> True if device is in error state:  NOP_ERROR or OP_ERROR """
        return substate in [self.SUBSTATE.NOT_OP_FAILURE, self.SUBSTATE.OP_FAILURE]
            
    
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        error_code: NV[ERROR] = ERROR.OK
        local: NV[bool] = False
        state: NV[int] = 0
        status: NV[int] = 0
        substate: NV[int] = 0
           
if __name__ == "__main__":
    s = ShutterStat( local=NC(parser=float) )
    assert s.Data(local=1).local == True
    assert s.config.local.suffix == "stat.bLocal" # this should not change because of the Default Type
    assert isinstance(s.local, N)
    s.is_closed
