from pydevmgr_core import (KINDS, NodeAlias, BaseNode, kjoin, ksplit, BaseInterface,  
                           BaseManager, upload,   get_class, record_class, GenDevice, 
                            BaseDevice, NodeVar, ObjectFactory
                           )
from pydevmgr_core.nodes import AllTrue

from . import io
from .eltdevice import EltDevice

from .tools import  get_txt, get_group
import logging

from collections import OrderedDict
from warnings import warn

from pydantic import BaseModel, root_validator, validator, AnyUrl
from typing import List, Type, Optional, Dict, Union, Iterable
import warnings



class ManagerServerConfig(BaseModel):
    fits_prefix: str = ""
    devices : List[str] = [] # list of device names for the record 
    cmdtout : int = 60000    # not yet used in pydevmgr 
    # ~~~~~~ Not Used by pydevmgr ~~~~~~~~~~~~~~~~~~~~~~
    req_endpoint    : str =  "zpb.rr://127.0.0.1:12082/"
    pub_endpoint    : str =  "zpb.ps://127.0.0.1:12345/"
    db_endpoint     : str =  "127.0.0.1:6379"
    db_timeout      : int =  2
    scxml           : str =  ""
    dictionaries    : List[str] =  []    
    


class DeviceIoConfig(BaseModel):
    type: str
    cfgfile: str
    path: Optional[str] = None
    
    def load(self):
        DeviceClass = get_class(KINDS.DEVICE, self.type)
        
        cfg = io.load_config(self.cfgfile)
        if self.path is not None:
            cfg = cfg[self.path]
        return DeviceClass.Config.parse_obj(cfg)


class ManagerConfig(BaseManager.Config):
    """ Manager Configuration Model """
    Server = ManagerServerConfig
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Elt"
    server_id: str = "" # for the record
    name: str = "" # if None takes the server_id 
    
    server: ManagerServerConfig = ManagerServerConfig()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Config of BaseModel see pydantic 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:
        extra = "allow"


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # root validator 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # first load the server on the fly if server_id is defined 
    # then, at the end, load the devices
    
    @root_validator(pre=True)
    def _pre_root_validator(cls, values):
        # load the server dictionary by loadding from the server_id keyword and its attached 
        # dictionary. As it was defined in eso software <v3
        if not "server" in values and "server_id" in values:
            server_id = values["server_id"]
            values["server"] = values.pop(server_id)
        return values  
    

     
    @classmethod
    def validate_extra(cls, name, extra, values):
        server = values['server']
        if name in server.devices:
            if "cfgfile" in extra:
                device_io = DeviceIoConfig( path = name, **extra )
                extra = device_io.load()
            elif "type" in extra:
                ExtraClass = get_class( KINDS.DEVICE, extra['type'] ).Config
                extra = ExtraClass.parse_obj(extra)
            else:
                extra = super().validate_extra(name, extra, values)
                if not isinstance(extra, BaseDevice.Config):
                    raise ValueError(f"{name} children is not a device")
        else:
            extra =  super().validate_extra(name, extra, values)         
        return extra

        
           
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        d = {'server_id':self.server_id, self.server_id:self.server.cfgdict()} 
        for name, ioc in self.devices.items():
            d[name] = ioc.cfgdict()
        return d

def open_elt_manager(cfgfile, key=None, path=None, prefix=""):
    """ Open a EltManager from a configuration file 

    ..note::
        
        pydevmgr is using yaml configuration file different to the ones used in ELT v3 
        However, do not wary, it will be transformed 

    Args:
        cfgfile: relative path to one of the $CFGPATH or absolute path to the yaml config file 
        key: Key of the created Manager 
        path (str, int, optional): 'a.b.c' will loock to cfg['a']['b']['c'] in the file. If int it will loock to the Nth
                                    element in the file
        prefix (str, optional): additional prefix added to the name or key

    Output:
        manager (EleManager) : elt manager handler
    """
    return EltManager.from_cfgfile(cfgfile, path=path, prefix=prefix, key=key)
    
    
class ManagerIOConfig(BaseModel):
    """ Config Model holding the I/O of a manager configuration """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    name      : str = ""
    cfgfile   : Optional[str] = None
    config    : ManagerConfig = None # built from cfgfile if None
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    @validator('config', always=True, pre=True)
    def load_config(cls, config, values):
        if config is None:
            cfgfile = values['cfgfile']
            if cfgfile:
                return ManagerConfig(name=values['name'], **io.load_config(cfgfile))
            else:
                return ManagerConfig(name=values['name'])
        return config
    


def load_manager_config(file_name: str, extrafile: Optional[str] =None) -> ManagerIOConfig:
    """ load a manager configuration from its yml file 
    
    Args:
        file_name (str): relative path to a configuration file 
                  The path is relative to one of the directory defined in the
                  $CFGPATH environmnet variable or it can be an absolute path  
    """
    return ManagerIOConfig(cfgfile=file_name, extrafile=extrafile)



## #######################################################
#
#   Some NodeAlias for the manager 
#   These are created in the .stat UaInterface property
#

class SubstateNodeAlias(NodeAlias):
    """ Attempt to build one substate out of severals """
    SUBSTATE = EltDevice.SUBSTATE
    
    def fget(self, *substates) -> int:        
        if not substates: return self.SUBSTATE.UNKNOWN
        first = substates[0]
        if all( s==first for s in substates):
            return int(first)
        return int(self.SUBSTATE.UNKNOWN)


def get_device_state_nodes(parent):
    return sum( [[d.stat.state,d.is_ignored] for d in  parent.devices ], [])

##
# The stat manager for stat interface will be build of NodeAliases only 
#  
@record_class
class ManagerStatInterface(BaseInterface):
    """ Special definition of Stat Interface for a Manager """
    class Config(BaseInterface.Config):
        type: str = "UaManagerStatInterface"
        
    STATE = EltDevice.STATE
    def __init__(self, key, devices, config=None, **kwargs):
        # config is a place holder
        super().__init__(key, config=config, **kwargs)
        self._devices = devices        
    
    @property
    def devices(self) -> Iterable:
        return self._devices
    
    @classmethod
    def prop(cls, name: Optional[str] = None):
        return cls.Property(cls, cls.new, name, config=cls.Config())
        
    @classmethod
    def new(cls, parent, name, config=None):
        """ build a :class:`ManagerStatInterface` from its parent context 
        
        parent is mostlikely a :class:`UaManager`
        
        requirement for the parent is to have: 
        
        - the devices() method
        """        
        return cls(kjoin(parent.key, name), list(parent.devices), config=config, **cls.new_args(parent, name, config))
    
    # The nodes is a function with signature func(parent) it is called by the .new class method 
    @NodeAlias.prop('state', nodes=get_device_state_nodes)
    def state(self, *states_ignore) -> int:
        """ return STATE.OP if all (not ignored) devices are in STATE.OP, STATE.NOTOP otherwhise """       
        states = [states_ignore[i] for i in range(0,len(states_ignore),2) if not states_ignore[i+1]]
                
        if all( s==self.STATE.OP for s in states ):
            return int(self.STATE.OP)
        return int(self.STATE.NOTOP)
    
    #state = DevicesState.prop('state')    
        
    @NodeAlias.prop("state_txt", ["state"])
    def state_txt(self, state: int) -> str:
        """ text representation of the state """        
        return get_txt(self.STATE(state))
    
    @NodeAlias.prop("state_group", ["state"])
    def state_group(self, state: int) -> state:
        """ group of the state """
        return get_group(self.STATE(state))

    class Data(BaseInterface.Data):
        state: NodeVar[int] = 0 
        state_txt: NodeVar[str] = ""
        state_group: NodeVar[str] = ""

@record_class            
class EltManager(BaseManager):
    """ UaManager object, handling several devices 
    
    .. note::
    
        Most likely the UaManager will be initialized by :meth:`UaManager.from_cfgfile` or its alias :func:`open_elt_manager`
    
       
    Args:
        key (str, optional): the key (prefix of all devices) of the manager
                   If None key is the 'server_id' defined inside the config dictionary or a random one is generated
        config (dict, :class:`ManagerConfig`, :class:`ManagerIOConfig`):  tion for the manager        
        
        devices (dict, optional) pairs of 
                    - name/ :class:`UaDevice` pairs 
                    - or  name/ :class:`DeviceConfig` pairs 
                Used when the manager is built without configuration file

    Exemples:

    ::

        from pydevmgr_elt import EltManager, Motor, Lamp
         
        devices = dict(
            motor = Motor('motor', address="opc.tcp://localhost:4840", prefix="MAIN.Motor1" ), 
            lamp = Lamp( 'lamp', address="opc.tcp://localhost:4840", prefix="MAIN.Lamp1"  )
        )
        mgr = EltManager('mgr',  devices )

        mgr.connect()
        mgr.motor.stat.pos_actual.get()
        # etc ...
        

    Or one can subclass the EltManager to configure the device layout configuration in the class 
    
    ::
        
         from pydevmgr_elt import EltManager, Motor, Lamp, Defaults, wait 
        
         class AitBench(EltManager):
            class Config( EltManager.Config, extra="forbid" ):
                motor: Defaults[Motor.Config] = Motor.Config( address="opc.tcp://myplc.local:4840", prefix="MAIN.Motor1" )
                lamp: Defaults[Lamp.Config] = Lamp.Config( address="opc.tcp://myplc.local:4840", prefix="MAIN.Lamp1" )
                server =  EltManager.Config.Server( devices=['motor', 'lamp'] )
                
                

         mgr = AitBench('mgr')
         mgr.connect()
         wait( mgr.init() )
         # etc ... 

    Above the devices list is the list of device names used in any function of mgr (like connect, init, reset etc...).
    For compatibility with ESO config file   this `device`` parameter is inside a ``server`` structure (pydandic model). This is not
    convenient but you can do whatever you want in your Config file and add the devices property of your class.  

    ::

         from pydevmgr_elt import EltManager, Motor, Lamp, CcsSim, Defaults, wait, BaseManager
         from typing import List    
         class AitBench(EltManager):
            class Config( BaseManager.Config, extra="forbid" ):
                motor: Defaults[Motor.Config] = Motor.Config( address="opc.tcp://myplc.local:4840", prefix="MAIN.Motor1" )
                lamp: Defaults[Lamp.Config] = Lamp.Config( address="opc.tcp://myplc.local:4840", prefix="MAIN.Lamp1" )
                ccs: CcsSim.Config = CcsSim.Config(address="opc.tcp://myplc.local:4840", prefix="MAIN.ccs_sim")
                devices: List[str] = ['lamp', 'motor']
             
            @property
            def devices(self):
                return [getattr(self, name) for name in self.config.devices]

         mgr = AitBench('mgr')
         mgr.devices
    
    Note, above I have added a ccs to show that even if it is not part of the devices list (used in connect, init,
    reset, enable, disable function) the ccs is still part of the manager :

    ::
        
        mgr.ccs.set_coordinates( 044534.0, -244567.0, 2000 )
        
    """
    Device = EltDevice # default device class
    Config = ManagerConfig    
    
    StatInterface = ManagerStatInterface    
    stat = StatInterface.prop('stat')
        
    def __init__(self, 
          key : Optional[str] = None, 
          config : Union[ManagerConfig,ManagerIOConfig, Dict] = None, 
          devices: Optional[Union[Dict[str, EltDevice.Config], Dict[str, EltDevice]]] = None, 
           **kwargs
        ) -> None:
       
        super().__init__(key, config=config, **kwargs)    
        if devices is not None:
            factory = ObjectFactory(EltDevice)
            for name, obj in devices.items():
                self.__dict__[name] = factory.build(self, name, obj)
            self.config.server.devices = list(devices)    

    def __dir__(self):
        lst = [d.name for d in self.devices]
        for sub in self.__class__.__mro__:
            for k in sub.__dict__:
                if not k.startswith('_'):
                    lst.append(k)
        return lst 
    
    @classmethod
    def from_cfgfile(cls, cfgfile, path="", prefix: str = '', key=None):
        return super().from_cfgfile( cfgfile, path=path, prefix=prefix, key=key)
    
    @property
    def key(self) -> str:
        return self._key
    
    # @property
    # def prefix(self):
    #     return ksplit(self._key)[0]
    
    @property
    def devices(self):
        return [getattr(self, dn) for dn in self.config.server.devices]


    @property
    def name(self) -> str:
        return ksplit(self._key)[1]
    
     
    def active_devices(self):
        """ return an iterator on active, aka, not-ignored devices """
        for d in self.devices:
            if not d.ignored.get():
                yield d
        
    def get_device(self, name: str) -> EltDevice:
        """ get device matching the name Raise ValueError if not found 
        Args:
           name (str): device name 
        """
        try:
            return self.devices[name]
        except KeyError:
            raise ValueError('Unknown device %r'%name)
    
  
    def device_names(self) -> list:
        """ return a list of child device names """
        return self.devices.names()
    
    ## These RPC should be on all devices
    def init(self) -> NodeAlias:
        """ Init all child devices 
        
        devices with a ignored flag will be ignored 
        
        Returns:
            all_initialised: a :class:`NodeAlias` which result in True when all devices are initialised
                             can be used in the :func:`pydevmgr.wait` function 
            
        Example:
           
           ::
           
               wait( mgr.init() )
        """
        nodes = [device.init() for device in self.devices if not device.is_ignored.get()]
        return AllTrue('init_all_finished', nodes)
        
    def enable(self) -> NodeAlias:
        """ Enable all child devices 
        
        devices with a ignored flag will be ignored 
        
        Returns:
            all_enabled: a :class:`NodeAlias` which result in True when all devices are enabled
                             can be used in the :func:`pydevmgr.wait` function 
            
        Example:
           
           ::
           
               wait( mgr.enable() )        
        
        """
        nodes = [device.enable() for device in self.devices if not device.is_ignored.get()]
        return AllTrue('enable_all_finished', nodes)
        
    def disable(self) -> NodeAlias:
        """ Disable all child devices 
        
        devices with a ignored flag will be ignored 
        
        Returns:
            all_disabled: a :class:`NodeAlias` which result in True when all devices are disabled 
                             can be used in the :func:`pydevmgr.wait` function 
            
        Example:
           
           ::
           
               wait( mgr.disable_all() )   
        """
        nodes = [device.disable() for device in self.devices if not device.is_ignored.get()]
        return AllTrue('disable_all_finished', nodes)        

    def reset(self) -> NodeAlias:
        """ Reset all child devices 
        
        devices with a ignored flag will be ignored 
        
        Returns:
            all_reseted: a :class:`NodeAlias` which result in True when all devices are reseted
                             can be used in the :func:`pydevmgr.wait` function 
            
        Example:
           
           ::
           
               wait( mgr.reset() )   
        
        """
        nodes = [device.reset() for device in self.devices if not device.is_ignored.get()]
        return AllTrue('reset_all_finished', nodes)        
    
    def configure(self) -> None:
        """ Configure all devices 
        
        devices with a ignored flag will be ignored 
        """
        conf = {}
        for device in self.devices:
            if not device.is_ignored.get():
                conf.update( device.get_configuration() )
        upload(conf)
    
    
    def ignore_all(self):
        """ set ignored flag to True for  all devices """
        for device in self.devices:
            device.is_ignored.set(True)
    
    def unignore_all(self):
        """ set ignored flag to False for  all devices """
        for device in self.devices:
            device.is_ignored.set(False)
    
    ### deprecated 
    def connect_all(self) -> None:
        """ Deprecated use connect instead  """
        warn(DeprecationWarning("connect_all method will be removed use connect "))
        return self.connect()
    def disconnect_all(self) -> None:
        """ Deprecated use disconnect instead  """
        warn(DeprecationWarning("disconnect_all method will be removed use disconnect "))
        return self.disconnect()
    def init_all(self) -> NodeAlias:
        """ Deprecated use init instead  """
        warn(DeprecationWarning("init_all method will be removed use init "))
        return self.init()
    def enable_all(self) -> NodeAlias:
        """ Deprecated use enable instead  """
        warn(DeprecationWarning("enable_all method will be removed use enable "))
        return self.enable()
    def disable_all(self) -> NodeAlias:
        """ Deprecated use disable instead  """
        warn(DeprecationWarning("disable_all method will be removed use disable "))
        return self.disable()
    def reset_all(self) -> NodeAlias:
        """ Deprecated use reset instead  """
        warn(DeprecationWarning("reset_all method will be removed use reset "))
        return self.reset()
    def configure_all(self) -> None:
        """ Deprecated use configure instead  """
        warn(DeprecationWarning("configure_all method will be removed use configure "))
        return self.configure()    
    
   
