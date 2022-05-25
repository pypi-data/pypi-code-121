from pydevmgr_vlt.devices.vltiodev.stat import VltIoDevStat as Stat
from pydevmgr_vlt.devices.vltiodev.ctrl  import VltIoDevCtrl as Ctrl

from pydevmgr_vlt.base import VltDevice
from pydevmgr_core import record_class, upload, BaseNodeAlias1
from typing import Optional, Union, Iterable, Dict, List
from pydantic import BaseModel

Base = VltDevice




class VltioDevCtrlConfig(BaseModel):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pass
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class VltioDevConfig(Base.Config):
    CtrlConfig = VltioDevCtrlConfig
    
    Ctrl = Ctrl.Config
    Stat = Stat.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "VltioDev"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    ctrl: Ctrl = Ctrl()
    stat: Stat = Stat()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@record_class
class VltAiChannel(BaseNodeAlias1):
    class Config(BaseNodeAlias1.Config):
        type = "VltAiChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.stat, f"ai_{config.channel_number}")
    
@record_class
class VltDiChannel(BaseNodeAlias1):
    class Config(BaseNodeAlias1.Config):
        type = "VltDiChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.stat, f"di_{config.channel_number}")

@record_class
class VltAoChannel(BaseNodeAlias1):
    class Config(BaseNodeAlias1.Config):
        type = "VltAoChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.ctrl, f"ao_{config.channel_number}")
    
@record_class
class VltDoChannel(BaseNodeAlias1):
    class Config(BaseNodeAlias1.Config):
        type = "VltDoChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.ctrl, f"do_{config.channel_number}")





@record_class
class VltIoDev(Base):
    """ ELt Standard VltioDev device """
    Config = VltioDevConfig
    Ctrl = Ctrl
    Stat = Stat
    
    AiChannel = VltAiChannel 
    AoChannel = VltAoChannel 
    DiChannel = VltDiChannel 
    DoChannel = VltDoChannel 

    class Data(Base.Data):
        Ctrl = Ctrl.Data
        Stat = Stat.Data
        
        ctrl: Ctrl = Ctrl()
        stat: Stat = Stat()
    
    def init(self):
        """ init the iodev  """
        upload({
            self.ctrl.execute: True, 
            self.ctrl.command: self.ctrl.COMMAND.INITIALISE
            })
        return self.stat.initialised
    
    def set_do(self, flags: Union[List[bool], Dict[int,bool]]):
        """ set digital output flags 
        
        Args:
            flags (list, or dict): list of bool or a dictionary of digital output index (starting from 0) and flag pair
             
        Exemple::

            io.set_do( [False]*8 ) # set all to zero 
            io.set_do( [True, False] ) # set do_0 and do_1 to True and False respectively (others are unchaged)
            io.set_do( {3:True, 4:True} ) # set do_4 and do_4 to True (others are unchanged)
        """
        if not isinstance(flags, dict):
            it = enumerate(flags)
        else:
            it = flags.items()

        ctrl = self.ctrl 
        n_f = { getattr(ctrl, "do_{}".format(i)):f for i,f in it }
        
        n_f.update( {ctrl.execute:True, ctrl.command :self.ctrl.COMMAND.ACTIVATE} )
        upload(n_f)
    
    def set_ao(self, values: Union[List[bool], Dict[int,bool]]):
        """ set degital output values 
        
        Args:
            flags (list, or dict): list of float or a dictionary of analog output index (starting from 0) and value  pair
             
        Exemple::

            io.set_ao( [0.0]*8 ) # set all to zero 
            io.set_ao( [32, 64] ) # set do_0 and do_1 to 32 and 64 respectively (others are unchaged)
            io.set_ao( {3:128, 4:128} ) # set do_4 and do_4 to 128 (others are unchanged)
        """

        if not isinstance(values, dict):
            it = enumerate(values)
        else:
            it = values.items()

        ctrl = self.ctrl 
        n_f = { getattr(ctrl, "do_{}".format(i)):f for i,f in it }
        
        n_f.update( {ctrl.execute:True, ctrl.command :self.ctrl.COMMAND.ACTIVATE} )
        upload(n_f)
    

    def get_do_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr( self.ctrl, f'do_{n}') for n in num]
        else:
            return getattr( self.ctrl, f'do_{num}')

    def get_ao_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr( self.ctrl, f'ao_{n}') for n in num]
        else:
            return getattr( self.ctrl, f'ao_{num}')

    def get_ai_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr(self.stat, f'ai_{n}') for n in num]
        else:
            return getattr(self.stat, f'ai_{num}')
     
    def get_di_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr( self.stat, f'di_{n}') for n in num]
        else:
            return getattr( self.stat, f'di_{num}')

if __name__ == "__main__":
    VltIoDev()
    print("OK")
