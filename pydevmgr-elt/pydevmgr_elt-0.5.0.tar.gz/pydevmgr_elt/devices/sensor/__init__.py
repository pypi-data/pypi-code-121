from pydevmgr_elt.devices.sensor.stat import SensorStat as Stat
from pydevmgr_elt.devices.sensor.cfg  import SensorCfg as Cfg
from pydevmgr_elt.devices.sensor.rpcs import SensorRpcs as Rpcs


from pydevmgr_elt.devices.sensor.aiChannels import AiChannels  
from pydevmgr_elt.devices.sensor.aoChannels import AoChannels  
from pydevmgr_elt.devices.sensor.diChannels import DiChannels  
from pydevmgr_elt.devices.sensor.doChannels import DoChannels  


from pydevmgr_elt.base import EltDevice
from pydevmgr_core import record_class, BaseNodeAlias1
from typing import Optional

Base = EltDevice


class SensorCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    timeout:          int  = 2000 

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class SensorConfig(Base.Config):
    CtrlConfig = SensorCtrlConfig
    
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config

    AiChannels = AiChannels.Config
    AoChannels = AoChannels.Config
    DiChannels = DiChannels.Config
    DoChannels = DoChannels.Config
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Sensor"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    cfg: Cfg = Cfg()
    stat: Stat = Stat()
    rpcs: Rpcs = Rpcs()
    
    aiChannels: AiChannels = AiChannels()
    aoChannels: AoChannels = AoChannels()
    diChannels: DiChannels = DiChannels()
    doChannels: DoChannels = DoChannels()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@record_class
class AiChannel(BaseNodeAlias1):
    """ NodeAlias1 to a analog input node iddentified from a number 

    Config: 
        channel_number (int)

    Example:
    
    ::

        from pydevmgr_elt import Sensor

        
        class MySensor(Sensor):
            class Config(Sensor.Config):
                temperature  = Sensor.AiChannel.Config(channel_number=3)
        
        my_sensor = MySensor()
        assert my_sensor.temperature.get() == my_sensor.aiChannels.ai3.get()
            
    """

    class Config(BaseNodeAlias1.Config):
        type = "AiChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.aiChannels, f"ai{config.channel_number}")

@record_class
class AoChannel(BaseNodeAlias1):
    """ NodeAlias1 to a analog output node iddentified from a number 

    Config: 
        channel_number (int)

    Example:
    
    ::

        from pydevmgr_elt import Sensor

        
        class MySensor(Sensor):
            class Config(Sensor.Config):
                intensity  = Sensor.AoChannel.Config(channel_number=3)

        my_sensor = MySensor()
        # then
        my_sensor.intensity.set(45)
        # is iddentical to 
        my_sensor.aoChannels.ao3.set(45)
        
    """

    class Config(BaseNodeAlias1.Config):
        type = "AoChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.aoChannels, f"ao{config.channel_number}")


@record_class
class DiChannel(BaseNodeAlias1):
    """ NodeAlias1 to a digital input node iddentified from a number 

    Config: 
        channel_number (int)

    Example:
    
    ::

        from pydevmgr_elt import Sensor

        
        class MySensor(Sensor):
            class Config(Sensor.Config):
                door_interlock = Sensor.DiChannel.Config(channel_number=3)
        
    """
    class Config(BaseNodeAlias1.Config):
        type = "DiChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.diChannels, f"di{config.channel_number}")


@record_class
class DoChannel(BaseNodeAlias1):
    """ NodeAlias1 to a analog output node iddentified from a number 

    Config: 
        channel_number (int)

    Example:
    
    ::

        from pydevmgr_elt import Sensor

        
        class MySensor(Sensor):
            class Config(Sensor.Config):
                switch  = Sensor.DoChannel.Config(channel_number=3)

        my_sensor = MySensor()
        # then
        my_sensor.witch.set(True)
        # is iddentical to 
        my_sensor.doChannels.do3.set(True)
        
    """

    class Config(BaseNodeAlias1.Config):
        type = "DoChannel"
        channel_number: int = 0
    @classmethod
    def _new_source_node(cls, parent, config):
        return getattr(parent.doChannels, f"do{config.channel_number}")






@record_class
class Sensor(Base):
    """ ELt Standard Sensor device """
    Config = SensorConfig
    Cfg = Cfg
    Stat = Stat
    Rpcs = Rpcs
    
    AiChannels = AiChannels
    AoChannels = AoChannels
    DiChannels = DiChannels
    DoChannels = DoChannels

    
    AiChannel = AiChannel
    AoChannel = AoChannel
    DiChannel = DiChannel
    DoChannel = DoChannel

    class Data(Base.Data):
        Cfg = Cfg.Data
        Stat = Stat.Data
        Rpcs = Rpcs.Data
        
        cfg: Cfg = Cfg()
        stat: Stat = Stat()
        rpcs: Rpcs = Rpcs()
    
 

if __name__ == "__main__":
    Sensor()
