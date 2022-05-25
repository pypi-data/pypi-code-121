from pydevmgr_core import  NodeAlias1, Defaults, NodeVar, record_class, BaseParser
from pydevmgr_vlt.base import VltDevice
from pydevmgr_vlt.devices._tools import _inc
from pydevmgr_ua import Int32
from enum import Enum
from pydantic import create_model
Base = VltDevice.Ctrl

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 

class COMMAND(int, Enum):
    NONE = 0
    INITIALISE = 1
    ACTIVATE = 2


N_AO, N_DO, N_NO, N_TO  = [8]*4



@record_class
class IoDevCommand(BaseParser):
    class Config(BaseParser.Config):
        type = "IoDevCommand"
    @staticmethod
    def parse(value, config):
        if isinstance(value, str):
            value =  getattr(COMMAND, value)
        return Int32(value)



# some dinamicaly created nodes
io_nodes = {}
for i in range(N_DO):
    io_nodes[f'do_{i}'] = (ND, NC(suffix= f'ctrl.arr_DO[{i}].bValue'))
for i in range(N_AO):
    io_nodes[f'ao_{i}'] = (ND, NC(suffix= f'ctrl.arr_AO[{i}].lrValue'))
for i in range(N_NO):
    io_nodes[f'no_{i}'] = (ND, NC(suffix= f'ctrl.arr_NO[{i}].nValue'))
for i in range(N_TO):
    io_nodes[f'to_{i}'] = (ND, NC(suffix= f'ctrl.arr_TO[{i}].sValue'))



class VltIoDevCtrl(Base):
    COMMAND = COMMAND
    class Config(create_model("Config",  __base__ = Base.Config, **io_nodes)):
        execute: ND = NC(suffix= 'ctrl.bExecute', parser= 'bool' )
        command: ND = NC(suffix= 'ctrl.nCommand', parser= 'IoDevCommand' )
        
    class Data(Base.Data):
        pass          

if __name__ == "__main__":
    VltIoDevCtrl()
    print("OK")

