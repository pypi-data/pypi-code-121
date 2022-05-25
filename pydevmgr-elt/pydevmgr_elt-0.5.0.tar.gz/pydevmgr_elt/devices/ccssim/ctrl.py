from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Interface

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class CcsSimCtrl(Base):
    class Config(Base.Config):
        temperature: ND = NC(suffix="ctrl.environment.temperature", parser=float)
        pressure: ND = NC(suffix="ctrl.environment.pressure", parser=float)
        humidity: ND = NC(suffix="ctrl.environment.humidity", parser=float)
        lapserate: ND = NC(suffix="ctrl.environment.lapserate", parser=float)
        wavelength: ND = NC(suffix="ctrl.wavelength", parser=float)
        dut: ND = NC(suffix="ctrl.dut", parser=float)

        alpha :    ND= NC(suffix="ctrl.meanCoordinates.alpha", parser=float)
        delta :    ND= NC(suffix="ctrl.meanCoordinates.delta", parser=float)
        epoch :    ND= NC(suffix="ctrl.meanCoordinates.epoch", parser=float)
        equinox :  ND= NC(suffix="ctrl.meanCoordinates.equinox", parser=float)
        pma :      ND= NC(suffix="ctrl.meanCoordinates.pma", parser=float)
        pmd :      ND= NC(suffix="ctrl.meanCoordinates.pmd", parser=float)
        radvel :   ND= NC(suffix="ctrl.meanCoordinates.radvel", parser=float)
        parallax : ND= NC(suffix="ctrl.meanCoordinates.parallax", parser=float)
        
        motion_x :   ND= NC(suffix="ctrl.motion.x", parser=float)
        motion_y :  ND= NC(suffix="ctrl.motion.y", parser=float)


 
    class Data(Base.Data):
        temperature: NV[float] = 0.0
        pressure: NV[float] = 0.0
        humidity: NV[float] = 0.0
        lapserate: NV[float] = 0.0
        wavelength: NV[float] = 0.0
        dut: NV[float] = 0.0    



