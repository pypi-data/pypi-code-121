from pydevmgr_core import   Defaults, NodeVar
from pydevmgr_elt.base import EltDevice

from enum import Enum
Base = EltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class AdcCfg(Base):
    class Config(Base.Config):
        pslope:             ND = NC(suffix="cfg.lrPslope")
        poffset:            ND = NC(suffix="cfg.lrPoffset")
        tslope:             ND = NC(suffix="cfg.lrTslope")
        toffset:            ND = NC(suffix="cfg.lrToffset")
        afactor:            ND = NC(suffix="cfg.lrAfactor")
        zdlimit:            ND = NC(suffix="cfg.lrZDlimit")
        minelev:            ND = NC(suffix="cfg.lrMinElev")
        latitude:           ND = NC(suffix="cfg.site.latitude")
        longitude:          ND = NC(suffix="cfg.site.longitude")
        trk_period:         ND = NC(suffix="cfg.nMinSkipCycles", parser="UaInt32")
        trk_threshold:      ND = NC(suffix="cfg.lrTrkThreshold")
        mot1_signoff:       ND = NC(suffix="cfg.unitCfg[1].nSignOff",parser="UaInt32")
        mot2_signoff:       ND = NC(suffix="cfg.unitCfg[2].nSignOff",parser="UaInt32")
        mot1_signauto:      ND = NC(suffix="cfg.unitCfg[1].nSignAuto",parser="UaInt32")
        mot2_signauto:      ND = NC(suffix="cfg.unitCfg[2].nSignAuto",parser="UaInt32")
        mot1_signphi:       ND = NC(suffix="cfg.unitCfg[1].nSignPhi",parser="UaInt32")
        mot2_signphi:       ND = NC(suffix="cfg.unitCfg[2].nSignPhi",parser="UaInt32")
        mot1_refoff:        ND = NC(suffix="cfg.unitCfg[1].lrRefOff")
        mot2_refoff:        ND = NC(suffix="cfg.unitCfg[2].lrRefOff")
        mot1_refauto:       ND = NC(suffix="cfg.unitCfg[1].lrRefAuto")
        mot2_refauto:       ND = NC(suffix="cfg.unitCfg[2].lrRefAuto")
        mot1_coffset:       ND = NC(suffix="cfg.unitCfg[1].lrCoffset")
        mot2_coffset:       ND = NC(suffix="cfg.unitCfg[2].lrCoffset")
        mot1_poffset:       ND = NC(suffix="cfg.unitCfg[1].lrPosOffset")
        mot2_poffset:       ND = NC(suffix="cfg.unitCfg[2].lrPosOffset")
        mot1_drotfactor:    ND = NC(suffix="cfg.unitCfg[1].lrDrotFactor")
        mot2_drotfactor:    ND = NC(suffix="cfg.unitCfg[2].lrDrotFactor")
        
    class Data(Base.Data):
        pslope:             NV[float]  =  0.0023
        poffset:            NV[float]  =  743.0
        tslope:             NV[float]  =  -0.0061
        toffset:            NV[float]  =  12.0
        afactor:            NV[float]  =  3.32
        zdlimit:            NV[float]  =  0.0174533
        minelev:            NV[float]  =  27.54
        latitude:           NV[float]  =  -0.429833092
        longitude:          NV[float]  =  1.228800386
        trk_period:         NV[int]  =  0 #cfg.nMinSkipCycles
        trk_threshold:      NV[float]  =  1.0
        mot1_signoff:       NV[int]    =  1
        mot2_signoff:       NV[int]    =  1
        mot1_signauto:      NV[int]    =  1
        mot2_signauto:      NV[int]    =  1
        mot1_signphi:       NV[int]    =  1
        mot2_signphi:       NV[int]    =  1
        mot1_refoff:        NV[float]  =  0.0
        mot2_refoff:        NV[float]  =  0.0
        mot1_refauto:       NV[float]  =  0.0
        mot2_refauto:       NV[float]  =  0.0
        mot1_coffset:       NV[float]  =  0.0
        mot2_coffset:       NV[float]  =  0.0
        mot1_poffset:       NV[float]  =  0.0
        mot2_poffset:       NV[float]  =  0.0
        mot1_drotfactor:    NV[float]  =  0.0
        mot2_drotfactor:    NV[float]  =  0.0

if __name__ == "__main__":
    AdcCfg()
