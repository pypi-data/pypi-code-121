
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

    NONE    		= 0
    
    NOTOP_NOTREADY    = 100
    NOTOP_READY		= 101
    NOTOP_ERROR		= 199
    
    OP_MONITORING	= 200
    OP_ERROR		= 299
    UNREGISTERED = -9999


# Add text definition to each constants, the definition is then accessible throught .txt attribute         

enum_group ({
        SUBSTATE.NONE                   : GROUP.UNKNOWN,
        SUBSTATE.NOTOP_NOTREADY         : GROUP.NOK,
        SUBSTATE.NOTOP_READY            : GROUP.NOK,
        SUBSTATE.NOTOP_ERROR            : GROUP.ERROR, 
  
        SUBSTATE.OP_MONITORING           : GROUP.BUZY, 
        SUBSTATE.OP_ERROR                : GROUP.ERROR,    
    })
    


class ERROR(int,  Enum):

    OK					= 0
    HW_NOT_OP			= 1			
    WRONG_CMD			= 2			
    INIT_FAILURE		= 3		

    NOT_INITIALISED		= 90
    ZERO_POINTER		= 100	# Simulator error_code
    
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute     
enum_txt ({
	ERROR.OK:			'OK',
	ERROR.HW_NOT_OP:	'ERROR: HW not in OP state',
    ERROR.INIT_FAILURE: 'ERROR: INIT failed', 
    })



    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class SensorStat(Base):
    # Add the constants to this class 
    ERROR = ERROR
    SUBSTATE = SUBSTATE
    
    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface


        state:          ND = NC(suffix="nState")
        substate:       ND = NC(suffix="nSubstate")
        local:          ND = NC(suffix="bLocal")
        error_code:     ND = NC(suffix="nErrorCode")

    @NodeAlias1.prop(node="substate")
    def is_ready(self, substate):
        """ Alias node: True if lamp is ready (substate NOTOP_READY_ON or NOTOP_READY_OFF) """
        return substate in [self.SUBSTATE.NOTOP_READY]
    


    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        error_code: NV[int] = 0
       

if __name__ == "__main__":
    SensorStat( local=NC(parser=float) )
