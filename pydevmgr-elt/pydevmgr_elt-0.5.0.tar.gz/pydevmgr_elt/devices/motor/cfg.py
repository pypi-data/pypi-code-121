from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt
from pydevmgr_elt.devices.motor.axis_type import  AXIS_TYPE # just needed to record axis type parser
from pydevmgr_elt.devices.motor.init_seq import INITSEQ
from enum import Enum
Base = EltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class MotorCfg(Base):
    AXIS_TYPE = AXIS_TYPE
    INITSEQ = INITSEQ
    class Config(Base.Config):
        active_low_index:   ND  =  NC(suffix='cfg.bArrActiveLow[3].bValue'  )
        active_low_lhw:     ND  =  NC(suffix='cfg.bArrActiveLow[1].bValue'  )
        active_low_lstop:   ND  =  NC(suffix='cfg.bArrActiveLow[0].bValue'  )
        active_low_ref:     ND  =  NC(suffix='cfg.bArrActiveLow[2].bValue'  )
        active_low_uhw:     ND  =  NC(suffix='cfg.bArrActiveLow[4].bValue'  )
        active_low_ustop:   ND  =  NC(suffix='cfg.bArrActiveLow[5].bValue'  )
        axis_type:          ND  =  NC(suffix='cfg.nAxisType',               parser='AxisType')
        backlash:           ND  =  NC(suffix='cfg.lrBacklash'               )
        brake:              ND  =  NC(suffix='cfg.bUseBrake'                )
        check_inpos:        ND  =  NC(suffix='cfg.bCheckInPos'              )
        disable:            ND  =  NC(suffix='cfg.bDisableAfterMove'        )
        exec_post_init:     ND  =  NC(suffix='cfg.bExecUserPostInit'        )
        exec_post_move:     ND  =  NC(suffix='cfg.bExecUserPostMove'        )
        exec_pre_init:      ND  =  NC(suffix='cfg.bExecUserPreInit'         )
        exec_pre_move:      ND  =  NC(suffix='cfg.bExecUserPreMove'         )
        init_seq1_action:   ND  =  NC(suffix='cfg.strArrInitSeq[1].nAction',   parser='UaInt32')
        init_seq1_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[1].lrValue1'   )
        init_seq1_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[1].lrValue2'   )
        init_seq2_action:   ND  =  NC(suffix='cfg.strArrInitSeq[2].nAction',   parser='UaInt32')
        init_seq2_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[2].lrValue1'   )
        init_seq2_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[2].lrValue2'   )
        init_seq3_action:   ND  =  NC(suffix='cfg.strArrInitSeq[3].nAction',   parser='UaInt32')
        init_seq3_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[3].lrValue1'   )
        init_seq3_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[3].lrValue2'   )
        init_seq4_action:   ND  =  NC(suffix='cfg.strArrInitSeq[4].nAction',   parser='UaInt32')
        init_seq4_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[4].lrValue1'   )
        init_seq4_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[4].lrValue2'   )
        init_seq5_action:   ND  =  NC(suffix='cfg.strArrInitSeq[5].nAction',   parser='UaInt32')
        init_seq5_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[5].lrValue1'   )
        init_seq5_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[5].lrValue2'   )
        init_seq6_action:   ND  =  NC(suffix='cfg.strArrInitSeq[6].nAction',   parser='UaInt32')
        init_seq6_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[6].lrValue1'   )
        init_seq6_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[6].lrValue2'   )
        init_seq7_action:   ND  =  NC(suffix='cfg.strArrInitSeq[7].nAction',   parser='UaInt32')
        init_seq7_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[7].lrValue1'   )
        init_seq7_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[7].lrValue2'   )
        init_seq8_action:   ND  =  NC(suffix='cfg.strArrInitSeq[8].nAction',   parser='UaInt32')
        init_seq8_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[8].lrValue1'   )
        init_seq8_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[8].lrValue2'   )
        init_seq9_action:   ND  =  NC(suffix='cfg.strArrInitSeq[9].nAction',   parser='UaInt32')
        init_seq9_value1:   ND  =  NC(suffix='cfg.strArrInitSeq[9].lrValue1'   )
        init_seq9_value2:   ND  =  NC(suffix='cfg.strArrInitSeq[9].lrValue2'   )
        init_seq10_action:  ND  =  NC(suffix='cfg.strArrInitSeq[10].nAction',  parser='UaInt32')
        init_seq10_value1:  ND  =  NC(suffix='cfg.strArrInitSeq[10].lrValue1'  )
        init_seq10_value2:  ND  =  NC(suffix='cfg.strArrInitSeq[10].lrValue2'  )
        lock:               ND  =  NC(suffix='cfg.bLock'                       )
        lock_pos:           ND  =  NC(suffix='cfg.lrLockPos'                   )
        lock_tolerance:     ND  =  NC(suffix='cfg.lrLockTol'                   )
        low_brake:          ND  =  NC(suffix='cfg.bActiveLowBrake'             )
        low_inpos:          ND  =  NC(suffix='cfg.bActiveLowInPos'             )
        max_pos:            ND  =  NC(suffix='cfg.lrMaxPosition'               )
        min_pos:            ND  =  NC(suffix='cfg.lrMinPosition'               )
        tout_init:          ND  =  NC(suffix='cfg.nTimeoutInit',               parser='UaInt32')
        tout_move:          ND  =  NC(suffix='cfg.nTimeoutMove',               parser='UaInt32')
        tout_switch:        ND  =  NC(suffix='cfg.nTimeoutSwitch',             parser='UaInt32')
        velocity:           ND  =  NC(suffix='cfg.lrDefaultVelocity'           )
    
    class Data(Base.Data):
        active_low_index:   NV[bool]   =  False
        active_low_lhw:     NV[bool]   =  False
        active_low_lstop:   NV[bool]   =  False
        active_low_ref:     NV[bool]   =  False
        active_low_uhw:     NV[bool]   =  False
        active_low_ustop:   NV[bool]   =  False
        axis_type:          NV[int]    =  0
        backlash:           NV[float]  =  0.0
        brake:              NV[bool]   =  False
        check_inpos:        NV[bool]   =  False
        disable:            NV[bool]   =  False
        exec_post_init:     NV[bool]   =  False
        exec_post_move:     NV[bool]   =  False
        exec_pre_init:      NV[bool]   =  False
        exec_pre_move:      NV[bool]   =  False
        init_seq10_action:  NV[int]    =  0
        init_seq10_value1:  NV[float]  =  0.0
        init_seq10_value2:  NV[float]  =  0.0
        init_seq1_action:   NV[int]    =  0
        init_seq1_value1:   NV[float]  =  0.0
        init_seq1_value2:   NV[float]  =  0.0
        init_seq2_action:   NV[int]    =  0
        init_seq2_value1:   NV[float]  =  0.0
        init_seq2_value2:   NV[float]  =  0.0
        init_seq3_action:   NV[int]    =  0
        init_seq3_value1:   NV[float]  =  0.0
        init_seq3_value2:   NV[float]  =  0.0
        init_seq4_action:   NV[int]    =  0
        init_seq4_value1:   NV[float]  =  0.0
        init_seq4_value2:   NV[float]  =  0.0
        init_seq5_action:   NV[int]    =  0
        init_seq5_value1:   NV[float]  =  0.0
        init_seq5_value2:   NV[float]  =  0.0
        init_seq6_action:   NV[int]    =  0
        init_seq6_value1:   NV[float]  =  0.0
        init_seq6_value2:   NV[float]  =  0.0
        init_seq7_action:   NV[int]    =  0
        init_seq7_value1:   NV[float]  =  0.0
        init_seq7_value2:   NV[float]  =  0.0
        init_seq8_action:   NV[int]    =  0
        init_seq8_value1:   NV[float]  =  0.0
        init_seq8_value2:   NV[float]  =  0.0
        init_seq9_action:   NV[int]    =  0
        init_seq9_value1:   NV[float]  =  0.0
        init_seq9_value2:   NV[float]  =  0.0
        lock:               NV[bool]   =  False
        lock_pos:           NV[float]  =  0.0
        lock_tolerance:     NV[float]  =  0.0
        low_brake:          NV[bool]   =  False
        low_inpos:          NV[bool]   =  False
        max_pos:            NV[float]  =  0.0
        min_pos:            NV[float]  =  0.0
        tout_init:          NV[int]    =  0
        tout_move:          NV[int]    =  0
        tout_switch:        NV[int]    =  0
        velocity:           NV[float]  =  0.0

if __name__=="__main__":
    MotorCfg()

           

