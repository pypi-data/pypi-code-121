from .eltinterface import EltInterface
from .eltnode import EltNode
from pydevmgr_core import NodeVar, NodeAlias1, Defaults, NodeAlias
from enum import Enum 
from .tools import enum_group, enum_txt, get_txt, get_group
from .config import GROUP


Base = EltInterface

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 


########################
### STATE 
class STATE(int, Enum):
    """ constant holder for device STATEs """
    NONE = 0
    NOTOP = 1
    OP = 2
    
    UNREGISTERED = -9999 # place holder for unregistered STATE
    
enum_group({
STATE.NONE  : GROUP.UNKNOWN,
STATE.NOTOP :  GROUP.NOK,
STATE.OP    :  GROUP.OK,
})


########################
### SUBSTATE 
class SUBSTATE(int, Enum):
    """ constant holder for device SUBSTATEs """
    # SUBSTATE are specific to each device
    # :TODO: is their common SUBSTATE for each device ? NOTOP_NOTREADY =  100
    #  NOTOP_READY = 101  ?
    NONE = 0
    NOTOP_NOTREADY = 100 # not sure these number are the same accros devices
    NOTOP_READY    = 101
    NOTOP_ERROR    = 199
    
    OP_ERROR =299
    
    UNREGISTERED = -9999 # place holder for unregistered SUBSTATE
    
enum_group({
  SUBSTATE.NONE                   : GROUP.UNKNOWN,
  SUBSTATE.NOTOP_NOTREADY         : GROUP.NOK,
  SUBSTATE.NOTOP_READY            : GROUP.NOK,
  SUBSTATE.NOTOP_ERROR            : GROUP.ERROR, 
  SUBSTATE.OP_ERROR               : GROUP.ERROR, 
})


    
########################
### ERROR  
class ERROR(int, Enum):
    """ constant holder for device ERRORs """
    OK	                   = 0
    HW_NOT_OP              = 1
    LOCAL                  = 2
    
    UNREGISTERED = -9999 # place holder for unregistered ERROR
    # etc...
enum_txt({
    ERROR.OK:		 'OK',
    ERROR.HW_NOT_OP: 'ERROR: TwinCAT not OP or CouplerState not mapped.',
    ERROR.LOCAL:	 'ERROR: Control not allowed. Motor in Local mode.',
    ERROR.UNREGISTERED: 'Unregistered ERROR'
        # etc ...
})

class StatInterface(EltInterface):
    
    ERROR = ERROR # needed for error_txt alias 
    SUBSTATE = SUBSTATE # needed for substate_txt node alias
    STATE = STATE 
    
    class Config(EltInterface.Config):
        state:             ND = NC(suffix="stat.nState")
        substate:          ND = NC(suffix="stat.nSubstate") 
        error_code:        ND = NC(suffix="stat.nErrorCode")

    @NodeAlias1.prop(node="state")
    def is_operational(self, state: int) -> bool:
        """ True if device is operational """
        return state == self.STATE.OP
    
    @NodeAlias1.prop(node="state")
    def is_not_operational(self, state: int) -> bool:
        """ True if device not operational """
        return state == self.STATE.NOTOP
    
    @NodeAlias1.prop(node="substate")
    def is_ready(self, substate: int) -> bool:
        """ True if device is ready """
        return substate == self.SUBSTATE.NOTOP_READY
    
    @NodeAlias1.prop(node="substate")
    def is_not_ready(self, substate: int) -> bool:
        """ True if device is not ready """
        return substate == self.SUBSTATE.NOTOP_NOTREADY
    
    @NodeAlias1.prop(node="substate")
    def is_in_error(self, substate: int) -> bool:
        """ -> True is device is in error state:  NOP_ERROR or OP_ERROR """
        return substate in [self.SUBSTATE.NOTOP_ERROR, self.SUBSTATE.OP_ERROR]
    
    @NodeAlias1.prop(node="substate")
    def substate_txt(self, substate: int) -> str:
        """ Return a text representation of the substate """
        return get_txt( self.SUBSTATE(substate) )
    
    @NodeAlias1.prop(node="substate")
    def substate_group(self, substate: int):
        """ Return the afiliated group of the substate """
        return get_group(self.SUBSTATE(substate))

    
    @NodeAlias1.prop(node="state")
    def state_txt(self, state: int) -> str:
        """ Return a text representation of the state """
        return get_txt( self.STATE(state) )

    @NodeAlias1.prop(node="state")
    def state_group(self, state: int):
        """ Return the afiliated group of the state """
        return get_group( self.STATE(state) )
    
    @NodeAlias1.prop(node="error_code")
    def error_txt(self, error_code: int) -> str:
        """ Return the text representation of an error or '' if no error """
        return get_txt( self.ERROR(error_code) )
    

    @NodeAlias.prop(nodes=["error_code", "error_txt"])
    def noerror_check(self, error_code, error_txt):
        """ Return always True but raise a ValueError in case of a non zero error code """
        if error_code:
            raise ValueError(f"Error [{self.key}]  error={error_code}: {error_txt}")
        return True

    @NodeAlias1.prop(node="error_code")
    def error_group(self, error_code: int) -> str:
        """ Return the text representation of an error or '' if no error """
        return GROUP.ERROR if error_code else GROUP.OK


    class Data(EltInterface.Data):
        """ Data Model class holding stat information of device """
        state : NodeVar[int] = 0
        substate: NodeVar[int] = 0
        error_code: NodeVar[int] = 0 
        
        ## Node Aliases 
        is_operational: NodeVar[bool] = False
        is_not_operational: NodeVar[bool] = False
        is_ready: NodeVar[bool] = False
        is_not_ready: NodeVar[bool] = False
        is_in_error: NodeVar[bool] = False
        
        substate_txt: NodeVar[str] = ""
        substate_group: NodeVar[str] = ""
        state_txt: NodeVar[str]  = ""
        state_group: NodeVar[str] = ""
        error_txt: NodeVar[str]  = ""  

