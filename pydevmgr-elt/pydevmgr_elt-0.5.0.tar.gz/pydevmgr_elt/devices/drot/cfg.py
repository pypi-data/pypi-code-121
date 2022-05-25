from pydevmgr_core import   Defaults, NodeVar
from pydevmgr_elt.devices.motor import Motor
Base = Motor.Cfg


N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class DrotCfg(Base):
    class Config(Base.Config):
        dir_sign: ND = NC(suffix='cfg.nDirSign', parser='UaInt32')
        focus_sign: ND = NC(suffix='cfg.nFocusSign', parser='UaInt32')
        trk_period: ND = NC(suffix='cfg.nMinSkipCycles', parser='UaInt32')

        stat_ref:           ND = NC(suffix="cfg.lrStatRef", parser=float)
        sky_ref:            ND = NC(suffix="cfg.lrSkyRef", parser=float)
        elev_ref:           ND = NC(suffix="cfg.lrElevRef", parser=float)
        user_ref:           ND = NC(suffix="cfg.lrUserRef", parser=float)
        user_par1:          ND = NC(suffix="cfg.lrUserPar1", parser=float)
        user_par2:          ND = NC(suffix="cfg.lrUserPar2", parser=float)
        user_par3:          ND = NC(suffix="cfg.lrUserPar3", parser=float)
        user_par4:          ND = NC(suffix="cfg.lrUserPar4", parser=float)
        latitude:           ND = NC(suffix="cfg.site.latitude", parser=float)
        longitude:          ND = NC(suffix="cfg.site.longitude", parser=float) 
        trk_threshold:      ND = NC(suffix="cfg.lrTrkThreshold", parser=float)

        active_low_index:   ND  =  NC(suffix='motor.cfg.bArrActiveLow[3].bValue'  )
        active_low_lhw:     ND  =  NC(suffix='motor.cfg.bArrActiveLow[1].bValue'  )
        active_low_lstop:   ND  =  NC(suffix='motor.cfg.bArrActiveLow[0].bValue'  )
        active_low_ref:     ND  =  NC(suffix='motor.cfg.bArrActiveLow[2].bValue'  )
        active_low_uhw:     ND  =  NC(suffix='motor.cfg.bArrActiveLow[4].bValue'  )
        active_low_ustop:   ND  =  NC(suffix='motor.cfg.bArrActiveLow[5].bValue'  )
        axis_type:          ND  =  NC(suffix='motor.cfg.nAxisType',               parser='AxisType')
        backlash:           ND  =  NC(suffix='motor.cfg.lrBacklash'               )
        brake:              ND  =  NC(suffix='motor.cfg.bUseBrake'                )
        check_inpos:        ND  =  NC(suffix='motor.cfg.bCheckInPos'              )
        disable:            ND  =  NC(suffix='motor.cfg.bDisableAfterMove'        )
        exec_post_init:     ND  =  NC(suffix='motor.cfg.bExecUserPostInit'        )
        exec_post_move:     ND  =  NC(suffix='motor.cfg.bExecUserPostMove'        )
        exec_pre_init:      ND  =  NC(suffix='motor.cfg.bExecUserPreInit'         )
        exec_pre_move:      ND  =  NC(suffix='motor.cfg.bExecUserPreMove'         )
        init_seq1_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[1].nAction',   parser='UaInt32')
        init_seq1_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[1].lrValue1'   )
        init_seq1_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[1].lrValue2'   )
        init_seq2_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[2].nAction',   parser='UaInt32')
        init_seq2_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[2].lrValue1'   )
        init_seq2_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[2].lrValue2'   )
        init_seq3_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[3].nAction',   parser='UaInt32')
        init_seq3_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[3].lrValue1'   )
        init_seq3_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[3].lrValue2'   )
        init_seq4_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[4].nAction',   parser='UaInt32')
        init_seq4_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[4].lrValue1'   )
        init_seq4_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[4].lrValue2'   )
        init_seq5_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[5].nAction',   parser='UaInt32')
        init_seq5_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[5].lrValue1'   )
        init_seq5_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[5].lrValue2'   )
        init_seq6_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[6].nAction',   parser='UaInt32')
        init_seq6_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[6].lrValue1'   )
        init_seq6_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[6].lrValue2'   )
        init_seq7_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[7].nAction',   parser='UaInt32')
        init_seq7_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[7].lrValue1'   )
        init_seq7_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[7].lrValue2'   )
        init_seq8_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[8].nAction',   parser='UaInt32')
        init_seq8_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[8].lrValue1'   )
        init_seq8_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[8].lrValue2'   )
        init_seq9_action:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[9].nAction',   parser='UaInt32')
        init_seq9_value1:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[9].lrValue1'   )
        init_seq9_value2:   ND  =  NC(suffix='motor.cfg.strArrInitSeq[9].lrValue2'   )
        init_seq10_action:  ND  =  NC(suffix='motor.cfg.strArrInitSeq[10].nAction',  parser='UaInt32')
        init_seq10_value1:  ND  =  NC(suffix='motor.cfg.strArrInitSeq[10].lrValue1'  )
        init_seq10_value2:  ND  =  NC(suffix='motor.cfg.strArrInitSeq[10].lrValue2'  )
        lock:               ND  =  NC(suffix='motor.cfg.bLock'                       )
        lock_pos:           ND  =  NC(suffix='motor.cfg.lrLockPos'                   )
        lock_tolerance:     ND  =  NC(suffix='motor.cfg.lrLockTol'                   )
        low_brake:          ND  =  NC(suffix='motor.cfg.bActiveLowBrake'             )
        low_inpos:          ND  =  NC(suffix='motor.cfg.bActiveLowInPos'             )
        max_pos:            ND  =  NC(suffix='motor.cfg.lrMaxPosition'               )
        min_pos:            ND  =  NC(suffix='motor.cfg.lrMinPosition'               )
        tout_init:          ND  =  NC(suffix='motor.cfg.nTimeoutInit',               parser='UaInt32')
        tout_move:          ND  =  NC(suffix='motor.cfg.nTimeoutMove',               parser='UaInt32')
        tout_switch:        ND  =  NC(suffix='motor.cfg.nTimeoutSwitch',             parser='UaInt32')
        velocity:           ND  =  NC(suffix='motor.cfg.lrDefaultVelocity'           )
  


    class Data(Base.Data):
        dir_sign: NV[int] = 0
        focus_sign: NV[int] = 0
        trk_period: NV[int] = 0

