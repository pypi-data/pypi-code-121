from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class PiezoCfg(Base):
    class Config(Base.Config):
        full_range1: ND = NC(suffix='cfg.nFullRange[0].nValue', parser='UaInt16')
        full_range2: ND = NC(suffix='cfg.nFullRange[1].nValue', parser='UaInt16')
        full_range3: ND = NC(suffix='cfg.nFullRange[2].nValue', parser='UaInt16')
        home1: ND = NC(suffix='cfg.nHome[0].nValue', parser='UaInt16')
        home2: ND = NC(suffix='cfg.nHome[1].nValue', parser='UaInt16')
        home3: ND = NC(suffix='cfg.nHome[2].nValue', parser='UaInt16')
        lower_limit1: ND = NC(suffix='cfg.nLimitLow[0].nValue', parser='UaInt16')
        lower_limit2: ND = NC(suffix='cfg.nLimitLow[1].nValue', parser='UaInt16')
        lower_limit3: ND = NC(suffix='cfg.nLimitLow[2].nValue', parser='UaInt16')
        max_on: ND = NC(suffix='cfg.nMaxOn', parser='UaInt32')
        num_axis: ND = NC(suffix='cfg.nNumAxes', parser='UaInt16')
        upper_limit1: ND = NC(suffix='cfg.nLimitHigh[0].nValue', parser='UaInt16')
        upper_limit2: ND = NC(suffix='cfg.nLimitHigh[1].nValue', parser='UaInt16')
        upper_limit3: ND = NC(suffix='cfg.nLimitHigh[2].nValue', parser='UaInt16')
        user_offset_input1: ND = NC(suffix='cfg.nUserOffsetBit_Get[0].nValue', parser='UaInt16')
        user_offset_input2: ND = NC(suffix='cfg.nUserOffsetBit_Get[1].nValue', parser='UaInt16')
        user_offset_input3: ND = NC(suffix='cfg.nUserOffsetBit_Get[2].nValue', parser='UaInt16')
        user_offset_output1: ND = NC(suffix='cfg.nUserOffsetBit_Set[0].nValue', parser='UaInt16')
        user_offset_output2: ND = NC(suffix='cfg.nUserOffsetBit_Set[1].nValue', parser='UaInt16')
        user_offset_output3: ND = NC(suffix='cfg.nUserOffsetBit_Set[2].nValue', parser='UaInt16')
        user_to_bit_input1: ND = NC(suffix='cfg.lrUser2Bit_Get[0].lrValue' )
        user_to_bit_input2: ND = NC(suffix='cfg.lrUser2Bit_Get[1].lrValue' )
        user_to_bit_input3: ND = NC(suffix='cfg.lrUser2Bit_Get[2].lrValue' )
        user_to_bit_output1: ND = NC(suffix='cfg.lrUser2Bit_Set[0].lrValue' )
        user_to_bit_output2: ND = NC(suffix='cfg.lrUser2Bit_Set[1].lrValue' )
        user_to_bit_output3: ND = NC(suffix='cfg.lrUser2Bit_Set[2].lrValue' )


    class Data(Base.Data):
        full_range1: NV[int] = 0
        full_range2: NV[int] = 0
        full_range3: NV[int] = 0
        home1: NV[int] = 0
        home2: NV[int] = 0
        home3: NV[int] = 0
        lower_limit1: NV[int] = 0
        lower_limit2: NV[int] = 0
        lower_limit3: NV[int] = 0
        max_on: NV[int] = 0
        num_axis: NV[int] = 0
        upper_limit1: NV[int] = 0
        upper_limit2: NV[int] = 0
        upper_limit3: NV[int] = 0
        user_offset_input1: NV[int] = 0
        user_offset_input2: NV[int] = 0
        user_offset_input3: NV[int] = 0
        user_offset_output1: NV[int] = 0
        user_offset_output2: NV[int] = 0
        user_offset_output3: NV[int] = 0
        user_to_bit_input1: NV[float] = 0.0
        user_to_bit_input2: NV[float] = 0.0
        user_to_bit_input3: NV[float] = 0.0
        user_to_bit_output1: NV[float] = 0.0
        user_to_bit_output2: NV[float] = 0.0
        user_to_bit_output3: NV[float] = 0.0



if __name__ == "__main__":
    PiezoCfg()
