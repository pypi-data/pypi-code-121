
from pydevmgr_ua import UaDevice 
from pydevmgr_core import record_class, upload
from pydevmgr_core.nodes import Local
from .vltinterface import VltInterface




class StatInterface(VltInterface):
    pass
class CfgInterface(VltInterface):
    pass
class CtrlInterface(VltInterface):
    pass






@record_class
class VltDevice(UaDevice):
    Node = VltInterface.Node
    Interface = VltInterface
    
    class Config(UaDevice.Config):
        Stat = StatInterface.Config
        Cfg = CfgInterface.Config
        Ctrl = CtrlInterface.Config 
        

        type = "VLT"
        ignored : bool = False
        stat: Stat = Stat()
        cfg: Cfg = Cfg()
        ctrl: Ctrl = Ctrl()
    
    class Data(UaDevice.Data):
        Stat = StatInterface.Data 
        Cfg = CfgInterface.Config
        Ctrl = CtrlInterface.Config 
        stat: Stat = Stat()
        cfg: Cfg = Cfg()
        ctrl: Ctrl = Ctrl()



    Stat = StatInterface
    Cfg = CfgInterface
    Ctrl = CtrlInterface

    
    is_ignored = Local.prop(default=False)
    

    def get_configuration(self, exclude_unset=True, **kwargs):
        """ return a node/value pair dictionary ready to be uploaded 
        
        The node/value dictionary represent the device configuration. 
        This is directly use by :func:`Device.configure` method. 
        
        This is a generic configuration dictionary and may not work on all devices. 
        This method need to be updated for special devices for instance.   
        
        Args:
            exclude_unset (optional, bool): Default is True. If True value that was left unset in 
                the config will not be included in the configuration
            \**kwargs : name/value pairs pointing to cfg.name node
                      This allow to change configuration on the fly
                      without changing the config file.             
        
        ::
        
            >>> upload( {**motor1.get_configuration(), **motor2.get_configuration()} ) 
        """
        # get values from the ctrl_config Config Model
        # do not include the default values, if they were unset, the PLC will use the default ones
        values = self.config.ctrl_config.dict(exclude_none=True, exclude_unset=exclude_unset)
        cfg_dict = { getattr(self.cfg, k):v for k,v in values.items()}
        cfg_dict[self.ignored] = self.config.ignored 
        cfg_dict.update({ getattr( self.cfg , k):v for k,v in kwargs.items()})
        return cfg_dict

    def configure(self, exclude_unset=True, **kwargs):
        """ Configure the whole device in the PLC according to what is defined in the config dictionary 
        
        Quick changes on configuration value can be done by keywords where each key must point to a 
        .cfg.name node. Note that the configuration (as written in file) is always used first before being 
        overwritten by \**kwargs. In other word kwargs are not changing the default configuration  
        
        Args:
            exclude_unset (optional, bool): Default is True. If True value that was left unset in 
                the config will not be included in the configuration

            \**kwargs :  name/value pairs pointing to cfg.name node
                        This allow to quickly change configuration on the fly
                        without changing the config file.
                          
        
        what it does is just:
        
        ::
        
           >>> upload( self.get_condifuration() ) 
        """
        # by default just copy the "ctrl_config" into cfg. This may not work for
        # all devices and should be customized  
        upload(self.get_configuration(exclude_unset=exclude_unset, **kwargs))
