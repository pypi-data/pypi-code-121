from pydevmgr_vlt.base import VltDevice
from pydevmgr_core import Defaults, NodeVar, NodeAlias, NodeAlias1
from pydevmgr_core.nodes import Opposite
from enum import Enum 
from typing import Optional 
from pydevmgr_vlt.devices.vltmotor.positions import PositionsConfig

Base = VltDevice.Stat

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 




class STATE(int, Enum):
    IDLE = 20
    RESET_AXIS = 30
    SET_POS = 40
    INIT = 50
    SAVE_TO_NOVRAM = 55
    CLEAR_NOVRAM = 57
    MOVE_ABS = 60
    MOVE_OPTIMISED = 61
    MOVE_VEL = 70
    CTRL_BRAKE = 75
    STOP = 80




class VltMotorStat(Base):
    STATE = STATE 
    class Config(Base.Config):
        mot_positions: PositionsConfig = PositionsConfig()
        state:                  ND  =  NC(suffix='nState'                     )
        pos_target:             ND  =  NC(suffix='stat.lrPosTarget'           )
        pos_actual:             ND  =  NC(suffix='stat.lrPosActual'           )
        vel_actual:             ND  =  NC(suffix='stat.lrVelActual'           )
        vel_target:             ND  =  NC(suffix='stat.lrVelTarget'           )
        axis_status:            ND  =  NC(suffix='stat.nAxisStatus'           )
        backlash_step:          ND  =  NC(suffix='stat.nBacklashStep'         )
        last_command:           ND  =  NC(suffix='stat.nLastCommand'          )
        error_code:             ND  =  NC(suffix='stat.nErrorCode'            )
        error_text:             ND  =  NC(suffix='stat.sErrorText'            )
        init_step:              ND  =  NC(suffix='stat.nInitStep'             )
        init_action:            ND  =  NC(suffix='stat.nInitAction'           )
        info_data1:             ND  =  NC(suffix='stat.nInfoData1'            )
        info_data2:             ND  =  NC(suffix='stat.nInfoData2'            )
        local:                  ND  =  NC(suffix='stat.bLocal'                )
        enabled:                ND  =  NC(suffix='stat.bEnabled'              )
        initialised:            ND  =  NC(suffix='stat.bInitialised'          )
        ref_switch:             ND  =  NC(suffix='stat.bRefSwitch'            )
        at_max_position:        ND  =  NC(suffix='stat.bAtMaxPosition'        )
        at_min_position:        ND  =  NC(suffix='stat.bAtMinPosition'        )
        limit_switch_positive:  ND  =  NC(suffix='stat.bLimitSwitchPositive'  )
        limit_switch_negative:  ND  =  NC(suffix='stat.bLimitSwitchNegative'  )
        brake_active:           ND  =  NC(suffix='stat.bBrakeActive'          )
        max_position:           ND  =  NC(suffix='stat.lrMaxPositionValue'    )
        min_position:           ND  =  NC(suffix='stat.lrMinPositionValue'    )
        mode:                   ND  =  NC(suffix='stat.nMode'                 )
        axis_ready:             ND  =  NC(suffix='stat.bAxisReady'            )
        moving_abs:             ND  =  NC(suffix='stat.bMovingAbs'            )
        moving_vel:             ND  =  NC(suffix='stat.bMovingVel'            )
        changing_vel:           ND  =  NC(suffix='stat.bChangingVel'          )
        

    @NodeAlias.prop("check", nodes=["error_code", "error_text"])
    def check(self, erc, ert):
        """ This node always return True but raise an error in case of device in error """
        if erc:
            raise RuntimeError(f"Error {erc}: {ert}")
        return True

    @NodeAlias1.prop( node="state")
    def state_txt(self, state):
        return self.STATE(state).name 

    @NodeAlias.prop( nodes=["state", "check"])
    def movement_finished(self, state, c):
        return state not in [self.STATE.MOVE_ABS, self.STATE.MOVE_OPTIMISED, self.STATE.MOVE_VEL, self.STATE.INIT]

    @NodeAlias.prop( nodes=["initialised", "check"])
    def initialisation_finished(self, initialised, c):
        return initialised

    @NodeAlias.prop( nodes=["enabled", "check"])
    def enable_finished(self, enabled, c):
        return enabled
    
    not_initialised = Opposite.prop(node="initialised")

    @NodeAlias1.prop(node="pos_actual")
    def pos_name(self, pos_actual):
        if not self.config.mot_positions: return ''
        positions = self.config.mot_positions
        tol = positions.tolerance
        for pname, pos in positions.positions.items():
            if abs( pos-pos_actual)<tol:
                return pname
        return ''

    # for this one we redefine the init so it does accept a mot_positions argument
    def __init__(self, *args, mot_positions: Optional[dict] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.mot_positions = mot_positions or PositionsConfig()

        
    # we need the mot_position from te parent (a Motor Device)
    # just add it to the dictionary create by  the super
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        try:
            mot_positions = parent.config.positions
        except AttributeError:
            mot_positions = {}
        d['mot_positions'] = mot_positions
        return d


    class Data(Base.Data):
        state:                  NV[int]    =  0
        pos_target:             NV[float]  =  0.0
        pos_actual:             NV[float]  =  0.0
        vel_actual:             NV[float]  =  0.0
        vel_target:             NV[float]  =  0.0
        axis_status:            NV[int]    =  0
        backlash_step:          NV[int]    =  0
        last_command:           NV[int]    =  0
        error_code:             NV[int]    =  0
        error_text:             NV[str]    =  ""
        init_step:              NV[int]    =  0
        init_action:            NV[int]    =  0
        info_data1:             NV[int]    =  0
        info_data2:             NV[int]    =  0
        local:                  NV[bool]   =  False
        enabled:                NV[bool]   =  False
        initialised:            NV[bool]   =  False
        ref_switch:             NV[bool]   =  False
        at_max_position:        NV[bool]   =  False
        at_min_position:        NV[bool]   =  False
        limit_switch_positive:  NV[bool]   =  False
        limit_switch_negative:  NV[bool]   =  False
        brake_active:           NV[bool]   =  False
        max_position:           NV[float]  =  0.0
        min_position:           NV[float]  =  0.0
        mode:                   NV[int]    =  0
        axis_ready:             NV[bool]   =  False
        moving_abs:             NV[bool]   =  False
        moving_vel:             NV[bool]   =  False
        changing_vel:           NV[bool]   =  False
           


if __name__ == "__main__":
    VltMotorStat()

