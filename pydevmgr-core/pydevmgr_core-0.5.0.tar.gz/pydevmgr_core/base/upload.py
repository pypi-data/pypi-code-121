from .node import NodesWriter, BaseNode
from .download import BaseDataLink

from typing import Union, Optional, Callable, Any, Dict 
import time 


class Uploader:
    """ An uploader object to upload data to the PLC 
    
    The values to upload is defined in a dictionary of node/value pairs. 
    
    Not sure their is a strong use case for this. Maybe if pydevmgr is used as server instead of client 
    
    Args:
        node_dict_or_datalink (dict, :class:`DataLink`):
             Dictionary of node/value pairs like ``{ motor.cfg.velocity : 4.3 }``
             Or a :class:`pydevmgr_core.DataLink` object.  
        callback (callable, optional): callback function after each upload
    
    Example:
        
    ::
    
        >>> values  = {mgr.motor1.velocity: 1.0, mgr.motor2.velocity: 2.0}
        >>> uploader = Uploader(values)
        >>> t = Thread(target=uploader.runner)
        >>> t.start()
        >>> uploader[mgr.motor1.velocity] = 1.4 # will be uploaded at next trhead cycle 
    
    ::
    
        from pydevmgr_elt import DataLink, NodeVar
        from pydantic import BaseModel 
        
        class Config(BaseModel):
            backlash: NodeVar[float] = 0.0
            disable: NodeVar[bool] = False
        
        >>> conf = Config()
        >>> Uploader( DataLink(mgr.motor1.cfg, conf) ).upload()
            
    .. seealso::
    
       :func:`upload`:  equivalent to Uploader(node_values).upload() 
       
       
    """
    def __init__(self, 
          node_dict_or_datalink: Union[Dict[BaseNode,Any], BaseDataLink], 
          callback: Optional[Callable] = None
        ) -> None:
        
        if node_dict_or_datalink is None:
            node_values = {}
            datalink = None
        elif isinstance(node_dict_or_datalink, BaseDataLink):
            datalink = node_dict_or_datalink
            node_values = {}
            datalink._upload_to(node_values)
        else:
            node_values = node_dict_or_datalink
            datalink = None    
            
        
        self.node_values = node_values 
        self.datalink = datalink
        self.callback = callback
    
    def __has__(self, node):
        return node in self._node_values
        
    def upload(self) -> None:
        """ upload the linked node/value dictionaries """
        if self.datalink:
            self.datalink._upload_to(self.node_values)
        
        NodesWriter(self.node_values).write() 
        if self.callback:
            self.callback()
                  
    def run(self, 
          period: float = 1.0, 
          stop_signal: Callable = lambda : False, 
          sleepfunc:  Callable = time.sleep
        ) -> None:
        """ Run the upload infinitly or until stop_signal is True 
        
        Args:
            period (float, optional): period of each upload cycle
            stop_signal (callable, optional): A function called at each cycle, if True the loop is break
                       and run returns    
        """
        while not stop_signal():
            s_time = time.time()
            self.upload()
            sleepfunc( max( period-(time.time()-s_time), 0))
    
    def runner(self, 
          period: float = 1.0, 
          stop_signal: Callable = lambda : False, 
          sleepfunc:  Callable = time.sleep
        ) -> Callable:
        """ return a function to updload 
        
        this is designed in particular to be used in a target Thread
        
        Args:
            period (float, optional): period of each upload cycle
            stop_signal (callable, optional): A function called at each cycle, if True the loop is break
                       and run returns
        
        Example:
            
            ::
            
                >>> values  = {mgr.motor1.velocity: 1.0, mgr.motor2.velocity: 2.0}
                >>> uploader = Uploader(values)
                >>> t = Thread(target=uploader.runner)
                >>> t.start()
                >>> values[mgr.motor1.velocity] = 1.2 # will be updated at next thread cycle
                               
        """           
        def run_func():
            self.run( period=period, sleepfunc=sleepfunc, stop_signal=stop_signal)
        return run_func
    


def upload(node_dict_or_datalink : Union[Dict[BaseNode,Any], BaseDataLink] ) -> None:
    """ write node values to the remotes
    
    Args:
        node_dict_or_datalink (dict):
             Dictionary of node/value pairs like  ``{ motor.cfg.velocity : 4.3 }``
             Or a :class:`pydevmgr_core.DataLink` object.  
                
    .. note:: 
        
        The input dictionary has pairs of node/value and not node.key/value      
    """
    NodesWriter(node_dict_or_datalink).write()    
