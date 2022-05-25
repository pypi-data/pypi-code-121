
from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt
from pydevmgr_elt.devices.motor.positions import PositionsConfig
from typing import Optional
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
    NONE =  0

    NOTOP_NOTREADY =  100
    NOTOP_READY = 101
    NOTOP_INITIALIZING = 102
    NOTOP_ABORTING = 107
    NOTOP_CLEARING_NOVRAM = 108

    NOTOP_ERROR =  199

    OP_STANDSTILL =216
    OP_MOVING = 217
    OP_SETTING_POS = 218
    OP_STOPPING = 219

    OP_ERROR =299
    
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute 
enum_group({
    SUBSTATE.NONE                   : GROUP.UNKNOWN,
    SUBSTATE.NOTOP_NOTREADY         : GROUP.NOK,
    SUBSTATE.NOTOP_READY            : GROUP.NOK,
    SUBSTATE.NOTOP_INITIALIZING     : GROUP.BUZY,
    SUBSTATE.NOTOP_ABORTING         : GROUP.BUZY,
    SUBSTATE.NOTOP_CLEARING_NOVRAM  : GROUP.BUZY,
    SUBSTATE.NOTOP_ERROR            : GROUP.ERROR, 
    SUBSTATE.OP_STANDSTILL          : GROUP.OK, 
    SUBSTATE.OP_MOVING              : GROUP.BUZY, 
    SUBSTATE.OP_SETTING_POS         : GROUP.BUZY,
    SUBSTATE.OP_STOPPING            : GROUP.BUZY,
    SUBSTATE.OP_ERROR               : GROUP.ERROR,    
})


class ERROR(int,  Enum):
    OK				      = _inc(0) # init the inc to zero
    HW_NOT_OP              = _inc()
    LOCAL                  = _inc()
    INIT_ABORTED           = _inc()
    TIMEOUT_INIT           = _inc()
    TIMEOUT_MOVE           = _inc()
    TIMEOUT_RESET          = _inc()
    TIMEOUT_SETPOS         = _inc()
    TIMEOUT_USER_PREINIT   = _inc()
    TIMEOUT_USER_POSTINIT  = _inc()
    TIMEOUT_USER_PREMOVE   = _inc()
    TIMEOUT_USER_POSTMOVE  = _inc()
    SETPOS                 = _inc()
    STOP                   = _inc()
    ABORT                  = _inc()
    SW_LIMIT_LOWER         = _inc()
    SW_LIMIT_UPPER         = _inc()
    BRAKE_ACTIVE           = _inc()
    BRAKE_ENGAGE           = _inc()
    BRAKE_DISENGAGE        = _inc()
    SWITCH_NOT_USED        = _inc()
    ENABLE                 = _inc()
    NOVRAM_READ            = _inc()
    NOVRAM_WRITE           = _inc()
    SWITCH_EXIT            = _inc()
    STOP_LIMITS_BOTH       = _inc()
    HW_LIMITS_BOTH         = _inc()
    IN_POS                 = _inc()
    LOCKED                 = _inc()
    SoE_ADS_ERROR          = _inc()
    SoE_SERCOS_ERROR       = _inc()

    # Simulator errors
    SIM_NOT_INITIALISED			= 90
    SIM_NULL_POINTER			= 100	

    # TwinCAT errors
    TC_VEL						= 16929	
    TC_NOT_READY_FOR_START		= 16933	
    TC_DISABLED_MOVE			= 16992	
    TC_BISECTION				= 17022	
    TC_MODULO_POS				= 17026	
    TC_STOP_ACTIVE				= 17135	
    TC_VEL_NEG					= 17241	
    TC_TARGET_LSW				= 17504	
    TC_TARGET_USW				= 17505	
    TC_FOLLOWING_ERROR			= 17744	
    TC_NOT_READY				= 18000	
    TC_IN_POS_6_SEC				= 19207	

    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute     
enum_txt ({
    ERROR.OK:				   'OK',
    ERROR.HW_NOT_OP:			 'ERROR: TwinCAT not OP or CouplerState not mapped.',
    ERROR.LOCAL:				 'ERROR: Control not allowed. Motor in Local mode.',
    ERROR.INIT_ABORTED:		     'ERROR: INIT command aborted.',
    ERROR.TIMEOUT_INIT:		     'ERROR: INIT timed out.',
    ERROR.TIMEOUT_MOVE:		     'ERROR: Move timed out.',
    ERROR.TIMEOUT_RESET:		 'ERROR: Reset timed out.',
    ERROR.TIMEOUT_SETPOS:		 'ERROR: Set Position timed out.',
    ERROR.TIMEOUT_USER_PREINIT:  'ERROR: User PRE-INIT timed out.',
    ERROR.TIMEOUT_USER_POSTINIT: 'ERROR: User POST-INIT timed out.',
    ERROR.TIMEOUT_USER_PREMOVE:  'ERROR: User PRE-MOVE timed out.',
    ERROR.TIMEOUT_USER_POSTMOVE: 'ERROR: User POST-MOVE timed out.',
    ERROR.SETPOS:				 'ERROR: Set Position failed.',
    ERROR.STOP:				     'ERROR: STOP failed.',
    
    ERROR.ABORT:			  'ERROR: Motion aborted.',
    ERROR.SW_LIMIT_LOWER:	  'ERROR: Lower SW Limit Exceeded.',
    ERROR.SW_LIMIT_UPPER:	  'ERROR: Upper SW Limit Exceeded.',
    ERROR.BRAKE_ACTIVE:		  'ERROR: Cannot move. Brake active.',
    ERROR.BRAKE_ENGAGE:		  'ERROR: Failed to engage brake.',
    ERROR.BRAKE_DISENGAGE:	  'ERROR: Failed to disengage brake.',
    ERROR.SWITCH_NOT_USED:	  'ERROR: Switch was not detected in previous INIT action.',
    ERROR.ENABLE:			  'ERROR: Failed to enable Axis.',
    ERROR.NOVRAM_READ:		  'ERROR: Failed to read from NOVRAM',
    ERROR.NOVRAM_WRITE:		  'ERROR: Failed to write to NOVRAM',
    ERROR.SWITCH_EXIT:		  'ERROR: Timeout on switch exit. Check nTimeoutSwitch.',
    ERROR.STOP_LIMITS_BOTH:	  'ERROR: Both LSTOP and USTOP limits active.',
    ERROR.HW_LIMITS_BOTH:	  'ERROR: Both limit switches LHW and UHW active.',
    ERROR.IN_POS:			  'ERROR: In-Pos switch not active at the end of movement.',
    ERROR.LOCKED:			  'ERROR: Motor Locked! Cannot move.',
    ERROR.SoE_ADS_ERROR:	  'ERROR: SoE ADS Error.',
    ERROR.SoE_SERCOS_ERROR:	  'ERROR: SoE Sercos Error.',

    ERROR.SIM_NOT_INITIALISED:  'ERROR: Simulator not initialised.',
    ERROR.SIM_NULL_POINTER:	    'ERROR: Simulator input parameter is a NULL pointer.',
    
    # Beckhoff TwinCAT most common errors
    ERROR.TC_VEL:				    'ERROR: Requested set velocity is not allowed.',
    ERROR.TC_NOT_READY_FOR_START:   'ERROR: Drive not ready during axis start. Maybe SW limits.',
    ERROR.TC_DISABLED_MOVE:		    'ERROR: Motor disabled while moving. Reset required!',
    ERROR.TC_BISECTION:			    'WARNING: Motion command could not be realized (BISECTION)',
    ERROR.TC_MODULO_POS:		    'ERROR: Target position >= full turn (modulo-period)',
    ERROR.TC_STOP_ACTIVE:		    'ERROR: Stop command still active. Axis locked. Reset required!',
    ERROR.TC_VEL_NEG:			    'ERROR: Set velocity not allowed (<=0)',
    ERROR.TC_TARGET_LSW:		    'ERROR: Target position beyond Lower Software Limit.',
    ERROR.TC_TARGET_USW:		    'ERROR: Target position beyond Upper Software Limit.',
    ERROR.TC_FOLLOWING_ERROR:	    'ERROR: Following error. Reset required!',
    ERROR.TC_NOT_READY:		        'ERROR: Drive not ready for operation.',
    ERROR.TC_IN_POS_6_SEC:	        'ERROR: In-position 6 sec timeout. Reset required!',
    
    ERROR.UNREGISTERED:        'ERROR: Unregistered Error'
})



    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 

class MotorStat(Base):
    # Add the constants to this class 
    ERROR = ERROR
    SUBSTATE = SUBSTATE
    


    class Config(Base.Config):
        # define all the default configuration for each nodes. 
        # e.g. the suffix can be overwriten in construction (from a map file for instance)
        # all configured node will be accessible by the Interface
        axis_brake: ND = NC(suffix='stat.bBrakeActive' )
        axis_enable: ND = NC(suffix='stat.bEnabled' )
        axis_info_data1: ND = NC(suffix='stat.nInfoData1' )
        axis_info_data2: ND = NC(suffix='stat.nInfoData2' )
        axis_inposition: ND = NC(suffix='stat.bInPosition' )
        axis_lock: ND = NC(suffix='stat.bLock' )
        axis_ready: ND = NC(suffix='stat.bAxisReady' )
        backlash_step: ND = NC(suffix='stat.nBacklashStep' )
        error_code: ND = NC(suffix='stat.nErrorCode' )
        init_action: ND = NC(suffix='stat.nInitAction' )
        init_step: ND = NC(suffix='stat.nInitStep' )
        initialised: ND = NC(suffix='stat.bInitialised' )
        local: ND = NC(suffix='stat.bLocal' )
        mode: ND = NC(suffix='stat.nMode' )
        pos_actual: ND = NC(suffix='stat.lrPosActual' )
        pos_error: ND = NC(suffix='stat.lrPosError' )
        pos_target: ND = NC(suffix='stat.lrPosTarget' )
        scale_factor: ND = NC(suffix='stat.lrScaleFactor' )
        signal_index: ND = NC(suffix='stat.signals[3].bActive' )
        signal_lhw: ND = NC(suffix='stat.signals[1].bActive' )
        signal_lstop: ND = NC(suffix='stat.signals[0].bActive' )
        signal_ref: ND = NC(suffix='stat.signals[2].bActive' )
        signal_uhw: ND = NC(suffix='stat.signals[4].bActive' )
        signal_ustop: ND = NC(suffix='stat.signals[5].bActive' )
        state: ND = NC(suffix='stat.nState' )
        status: ND = NC(suffix='stat.nStatus' )
        substate: ND = NC(suffix='stat.nSubstate' )
        vel_actual: ND = NC(suffix='stat.lrVelActual' )
    
        mot_positions: Optional[PositionsConfig] = None
        
    # for this one we redefine the init so it does accept a mot_positions argument
    def __init__(self, *args, mot_positions: Optional[dict] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.mot_positions = mot_positions or PositionsConfig()

        
    # we need the mot_position from te parent (a Motor Device)
    # just add it to the dictionary create by  the super
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name,  config)
        try:
            mot_positions = parent.config.positions
        except AttributeError:
            mot_positions = {}
        d['mot_positions'] = mot_positions
        return d

    @NodeAlias1.prop(node="substate")
    def is_moving(self, substate):
        """ -> True is axis is moving """
        return substate == self.SUBSTATE.OP_MOVING

    @NodeAlias1.prop(node="substate")
    def is_standstill(self,  substate):
        """ -> True is axis is standstill """
        return substate == self.SUBSTATE.OP_STANDSTILL
    
    
    @NodeAlias1.prop(node="pos_actual")
    def pos_name(self, pos_actual):
        if not self.config.mot_positions: return ''
        positions = self.config.mot_positions
        tol = positions.tolerance
        for pname, pos in positions.positions.items():
            if abs( pos-pos_actual)<tol:
                return pname
        return ''
  
  

    # We can add some nodealias to compute some stuff on the fly 
    # If they node to be configured one can set a configuration above 
    
    # Node Alias here     
    # Build the Data object to be use with DataLink, the type and default are added here 
    class Data(Base.Data):
        axis_brake: NodeVar[bool] = False
        axis_enable: NodeVar[bool] = False
        axis_info_data1: NodeVar[int] = 0
        axis_info_data2: NodeVar[int] = 0
        axis_inposition: NodeVar[bool] = False
        axis_lock: NodeVar[bool] = False
        axis_ready: NodeVar[bool] = False
        backlash_step: NodeVar[int] = 0
        error_code: NodeVar[int] = 0
        init_action: NodeVar[int] = 0
        init_step: NodeVar[int] = 0
        initialised: NodeVar[bool] = False
        local: NodeVar[bool] = False
        mode: NodeVar[int] = 0
        pos_actual: NodeVar[float] = 0.0
        pos_error: NodeVar[float] = 0.0
        pos_target: NodeVar[float] = 0.0
        scale_factor: NodeVar[float] = 0.0
        signal_index: NodeVar[bool] = False
        signal_lhw: NodeVar[bool] = False
        signal_lstop: NodeVar[bool] = False
        signal_ref: NodeVar[bool] = False
        signal_uhw: NodeVar[bool] = False
        signal_ustop: NodeVar[bool] = False
        state: NodeVar[int] = 0
        status: NodeVar[int] = 0
        substate: NodeVar[int] = 0
        vel_actual: NodeVar[float] = 0.0
        # ~~~~~~~~Add some node alis as well 
        is_moving: NodeVar[bool] = False
        is_standstill: NodeVar[bool] = False
        pos_name: NodeVar[str] = ""


if __name__ == "__main__":
    MotorStat( local=NC(parser=float) )
    print("OK")
