from typing import Optional
from .serial_node import BaseSerialNode 
from .serial_rpc import BaseSerialRpc 
from .serial_interface import SerialInterface
from enum import Enum
import serial as sr

from pydevmgr_core import BaseDevice

class BITSIZE(int, Enum):
    FIVE  = sr.FIVEBITS
    SIX   = sr.SIXBITS
    SEVEN = sr.SEVENBITS
    EIGHT = sr.EIGHTBITS

class PARITY(str, Enum):
    NONE  = sr.PARITY_NONE
    EVEN  = sr.PARITY_EVEN
    ODD   = sr.PARITY_ODD 
    MARK  = sr.PARITY_MARK
    SPACE = sr.PARITY_SPACE

class STOPBITS(float, Enum):
    ONE = sr.STOPBITS_ONE
    ONE_POINT_FIVE = sr.STOPBITS_ONE_POINT_FIVE
    TWO = sr.STOPBITS_TWO

# port is left in purpose do not add it 
_serials_args= set(['baudrate', 'bytesize', 'parity', 'stopbits', 'timeout', 
    'xonxoff', 'rtscts', 'write_teimout',
    'inter_byte_teimout', 'exclusive' ])

 
class SerialDevice(BaseDevice):
    class Config(BaseDevice.Config):
        port : str = ""
        baudrate: int = 9600
        bytesize:  BITSIZE = BITSIZE.EIGHT
        parity: PARITY = PARITY.NONE
        stopbits: STOPBITS = STOPBITS.ONE
        timeout: Optional[float] = None
        xonxoff: bool = False 
        rtscts: bool = False
        write_timeout: Optional[float] = None 
        inter_byte_timeout: Optional[float] = None
        exclusive: Optional[bool] = None
       
        
    Node = BaseSerialNode
    Rpc = BaseSerialRpc
    Interface = SerialInterface 
    
    BITSIZE = BITSIZE
    PARITY = PARITY
    STOPBITS = STOPBITS
 
    _com = None                
    def __init__(self, 
           key: Optional[str] = None, 
           config: Optional[Config] = None,
           com: Optional[sr.Serial] = None,             
           **kwargs
        ) -> None:     
        super().__init__(key, config=config, **kwargs)
        self._com = self.new_com(self.config, com)
    
    
    @classmethod
    def new_com(cls, config: Config, com: Optional[sr.Serial]=None):
        if com is None:
            com = sr.Serial( **config.dict( include=_serials_args ))
            # add the port after so the connection is not yet established
            com.port = config.port
        return com 
    
    @classmethod
    def new_args(cls, parent, name,  config):
        d = super().new_args(parent, name, config)
        if isinstance( parent, (SerialDevice, SerialInterface) ):
            d.update(com=parent.com)
        return d
    
    
    @property
    def com(self):
        return self._com 
    
    def connect(self):
        """connect the serial com """
        self._com.open()
    
    def disconnect(self):
        """disconnect serial com """
        self._com.close()
    
    
