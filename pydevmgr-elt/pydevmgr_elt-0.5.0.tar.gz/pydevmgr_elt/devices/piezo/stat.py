
from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt
from typing import Any
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
    NONE                  =   0
    NOTOP_NOTREADY		  = 100
    NOTOP_READY		      = 101
    NOTOP_INITIALISING	  = 102
    NOTOP_ERROR			  = 199
    OP_DISABLING		  = 205
    OP_POS                = 203
    OP_AUTO               = 204
    OP_ERROR			  = 299
    
    UNREGISTERED = -9999
    
enum_group ( {
    SUBSTATE.NONE                   : GROUP.UNKNOWN,
    SUBSTATE.NOTOP_NOTREADY         : GROUP.NOK,
    SUBSTATE.NOTOP_READY            : GROUP.NOK,
    SUBSTATE.NOTOP_INITIALISING     : GROUP.BUZY,
    SUBSTATE.NOTOP_ERROR            : GROUP.ERROR, 
    SUBSTATE.OP_DISABLING		   : GROUP.BUZY,
    SUBSTATE.OP_POS                 : GROUP.OK, 
    SUBSTATE.OP_AUTO                : GROUP.OK, 
    SUBSTATE.OP_ERROR               : GROUP.ERROR, 
})

### ##############
# ERROR
class ERROR(int, Enum):
    OK		      = 0
    HW_NOT_OP     = 1			
    ON_FAILURE    = 2
    MAXON         = 3
    OUT_OF_RANGE  = 4
    USER2BIT_ZERO = 5
	
	# Simulator errors
    NOT_INITIALISED		= 90
    ZERO_POINTER		= 100	
    
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute     
enum_txt ({
    ERROR.OK:				 'OK',
    ERROR.HW_NOT_OP:		 'ERROR: TwinCAT not in OP state or CouplerState not mapped.',
    ERROR.ON_FAILURE:        'ERROR: Piezo HW failure',
    ERROR.MAXON:             'ERROR: Maximum ON time exceeded.',
    ERROR.OUT_OF_RANGE:      'ERROR: Piezo set position out of range',
    ERROR.USER2BIT_ZERO:     'ERROR: cfg.lrUser2Bit has zero value.',
    
    ERROR.UNREGISTERED:       'ERROR: Unregistered Error'
})




    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class PiezoStat(Base):
    # Add the constants to this class 
    ERROR = ERROR
    SUBSTATE = SUBSTATE
    
    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        actual_pos_bit1: ND = NC(suffix='stat.nActPosBit[0].nValue' )
        actual_pos_bit2: ND = NC(suffix='stat.nActPosBit[1].nValue' )
        actual_pos_bit3: ND = NC(suffix='stat.nActPosBit[2].nValue' )
        actual_pos_user1: ND = NC(suffix='stat.lrActPosUsr[0].lrValue' )
        actual_pos_user2: ND = NC(suffix='stat.lrActPosUsr[1].lrValue' )
        actual_pos_user3: ND = NC(suffix='stat.lrActPosUsr[2].lrValue' )
        error_code: ND = NC(suffix='stat.nErrorCode' )
        local: ND = NC(suffix='stat.bLocal' )
        mon_act_pos_bit1: ND = NC(suffix='stat.monSetPosBit_0' )
        mon_act_pos_bit2: ND = NC(suffix='stat.monSetPosBit_1' )
        mon_act_pos_bit3: ND = NC(suffix='stat.monSetPosBit_2' )
        mon_act_pos_usr1: ND = NC(suffix='stat.monActPosUsr_0' )
        mon_act_pos_usr2: ND = NC(suffix='stat.monActPosUsr_1' )
        mon_act_pos_usr3: ND = NC(suffix='stat.monActPosUsr_2' )
        state: ND = NC(suffix='stat.nState' )
        substate: ND = NC(suffix='stat.nSubstate' )

    
    @NodeAlias1.prop(node="substate")
    def is_auto(self, substate: int) -> bool:
        """ -> True is axis is in auto mode """
        return substate == self.SUBSTATE.OP_AUTO
    
    @NodeAlias1.prop("substate")
    def is_pos(self, substate: int) -> bool:
        """ -> True is axis is in pos mode """
        return substate == self.SUBSTATE.OP_POS
    

    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        actual_pos_bit1: NV[int] = 0
        actual_pos_bit2: NV[int] = 0
        actual_pos_bit3: NV[int] = 0
        actual_pos_user1: NV[float] = 0.0
        actual_pos_user2: NV[float] = 0.0
        actual_pos_user3: NV[float] = 0.0
        error_code: NV[int] = 0
        local: NV[bool] = False
        mon_act_pos_bit1: NV[Any] = None
        mon_act_pos_bit2: NV[Any] = None
        mon_act_pos_bit3: NV[Any] = None
        mon_act_pos_usr1: NV[Any] = None
        mon_act_pos_usr2: NV[Any] = None
        mon_act_pos_usr3: NV[Any] = None
        state: NV[int] = 0
        substate: NV[int] = 0
        is_auto: NV[bool] = False
        is_pos: NV[bool] = False



if __name__ == "__main__":
    PiezoStat( )
