from pydantic import BaseModel

from .datamodel import DataLink 
from .download import Downloader

from typing import Any, Optional, Callable
import math 
import time
import traceback
from threading import Thread
from enum import Enum 




class MonitorError(RuntimeError):
    pass


class StopMonitor(RuntimeError):
    pass

class NextSetup(RuntimeError):
    pass


class BaseMonitor:
    """ Base class for a monitoring or script system 
    
    A Monitor object define an update method in order to handle new data updated 
    separatly from a distant server for instance.
    
    The update method returns an integer to whatever master is controling the monitor,
    the rule is:
        CONTININUE 0  -> continue the monitoring
        NEXT -1 -> execute the next movement (for instance for a new hardware setup) then 
                  continue monitoring 
        END -2 -> Finish the monitoring 
        All other positive integger are handled as error code
    
    The update method has the signature: ``monitor.update(device, data)``
    
    The start method,  signature ``monitor.start(device, data )`` is getting ready the Monitor 
    The next method, signature ``monitor.next(device, data )`` is applying, if needed a new setup 
                    before continuing the update
    The end method, signature ``monitor.end(device, data, error=None)`` is closing properlly the Monitor. 
                    It can be called with an Exception

    The update_failure, signature( data, err), this function is called each time a data download failed with an
             exception (``err`` argument). If a succesfull download follows a failure the function is called again 
             one time with err=None. This can handle the cases when for instance the connection to a distant server
             is lost for a laps of time. 

    Two other classes are used to handle the monitor easely: 
        - MonitorConnection 
            It does the connect the Monitor to a :class:`pydevmgr_core.Downloader` object
            The update is done at each downloader update
        - MonitorRunner
            It runs the monitor update in a loop 
    
    """
    class STEP(int, Enum):
        CONTINUE = 0 
        NEXT = -1 
        END  = -2
        # other are ERROR code should be >0

    class ERROR(int, Enum):
        pass
        
    class Config(BaseModel):
        pass   
    
    class Data(BaseModel):
        pass
    
    StopMonitor = StopMonitor
    NextSetup = NextSetup
    

    def __init__(self, config=None, **kwargs):
        self.config = self.parse_config(config, **kwargs)
        

    @classmethod
    def parse_config(cls, __config__=None, **kwargs):
        if __config__ is None:
            return cls.Config(**kwargs)
        if isinstance(__config__ , cls.Config):
            return __config__
        if isinstance(__config__, dict):
            d = {**__config__, **kwargs} 
            return cls.Config( **d )
        raise ValueError(f"got an unexpected object for config : {type(__config__)}")
    
    def runner(self, device, data=None):
        return MonitorRunner(self, device, data)     
    
    def connector(self, device, data=None):
        return MonitorConnection(self, device, data)
     
    def start(self, 
          device: Any, 
          data: Data, 
         ) -> None:
        pass
    
    def next(self, 
          device: Any, 
          data: Data, 
        ) -> None:
        pass

    def end(self, 
          device: Any,
          data: Data, 
          error: Optional[Exception] = None
        ) -> None:
        return None 
     
    def update(self, data: Data):
        raise NextSetup
    
    def update_failure(self, data: Data, err: Exception):
        if err:
            raise StopMonitor


class MonitorConnection:
    def __init__(self, 
          monitor: BaseMonitor,
          device: Any, 
          data: BaseModel = None
        ) -> None:
        if data is None:
            data = monitor.Data()
        
        self.monitor = monitor
        self.device = device
        self.data = data
        
        self._connection = None
        self._callback_thread = Thread()

        self._is_alive_flag = False
         
    
    def _build_callback_function(self):
        def _monitor_callback_function():
            # The monitor.next method is beeing executed 
            if self._callback_thread.is_alive():
                return

            try:
                self.monitor.update( self.data )
            except StopMonitor:
                self.disconnect()
            except NextSetup:
                self._callback_thread = Thread(target=self.monitor.next, args=(self.device, self.data) )
                self._callback_thread.start()
            except Exception as er:
                self.disconnect( er )


        return _monitor_callback_function
    
    
    def _build_callback_failure_function(self):
        def _callback_failure(failure_error):
            if self._callback_thread.is_alive():
                return

            try:
                self.monitor.update_failure( self.data, failure_error )
            except StopMonitor:
                self.disconnect()
            except NextSetup:
                self._callback_thread = Thread(target=self.monitor.next, args=(self.device, self.data) )
                self._callback_thread.start()
            except Exception as er:
                self.disconnect( er )
   
        return _callback_failure
                
    

    def is_alive(self):
        return self._is_alive_flag 

    def connect(self, downloader: Downloader,  link_failure=True):
        self.disconnect()
        
            
        self.monitor.start( self.device, self.data)
        
        data_link = DataLink( self.device, self.data)
        
        self._connection = downloader.new_connection()
        self._connection.add_datalink( data_link )
        
        normal_callback = self._build_callback_function()
        self._connection.add_callback( normal_callback )
        
        if link_failure:
            failure_callback = self._build_callback_failure_function()
            self._connection.add_failure_callback( failure_callback )    
        self._is_alive_flag = True
        
        
    def disconnect(self, error=None):
        if self._connection:
            self._connection.disconnect()
        self._is_alive_flag = False
        error_is_cleared_flag = self.monitor.end(self.device, self.data, error)
        if error and not error_is_cleared_flag:
            traceback.print_exc()
            raise error



class MonitorRunner:
    def __init__(self, 
         monitor: BaseMonitor, 
         device: Any,         
         data: Optional[BaseModel] = None
        ) -> None:
        if data is None:
            data  = monitor.Data()
            
        self.monitor = monitor 
        self.device = device
        
        self.data = data
        self._is_alive_flag = False 
    

    def _download_and_update_with_failure(self, data_link: DataLink, download_failed_pointer):
               
        try:
            data_link.download()
        except Exception as e:
            self.monitor.update_failure(self.data, e)
            download_failed_pointer[0] = True
        else:
            if download_failed_pointer[0]:
                download_failed_pointer[0] = False
                self.monitor.update_failure(self.data, None)

            self.monitor.update(self.data)

    
    def _download_and_update(self, data_link: DataLink, download_failed_pointer): 
        data_link.download()
        self.monitor.update(self.data)
            
    
    def _end_with_error(self, error):
        try:
            error_is_cleared_flag = self.monitor.end(self.device, self.data, error)
        finally:
            self._is_alive_flag = False
        if not error_is_cleared_flag:
            traceback.print_exc()
            raise error    
 
    def _end_without_error(self):
        try:
            self.monitor.end(self.device, self.data, None)
        finally:
            self._is_alive_flag = False


    def run(self, 
          period: float = 1, 
          stop_signal: Callable = lambda: False , 
          link_failure: bool = True
        ) -> None:

        data_link = DataLink( self.device, self.data )
        data_link.download()
        
        self.monitor.start(self.device, self.data)
        
        download_failed_pointer = [False]
        
        if link_failure:
            download_and_update = self._download_and_update_with_failure
        else:
            download_and_update = self._download_and_update

        
        self._is_alive_flag = True
        while not stop_signal():
                            
            tic = time.time()
                
            try:
                download_and_update(data_link, download_failed_pointer)
            except NextSetup:
                self.monitor.next( self.device, self.data)
            except StopMonitor:
                break 
            except Exception as er:
                self._end_with_error(er)
                return 
            
            toc = time.time()
            time.sleep( max(period-(toc-tic), 1e-6) ) # This avoid negative sleepp time
        
        self._end_without_error()


    def is_alive(self):
        return self._is_alive_flag 
    

    def target_function(self, 
            period: float = 1.0, 
            stop_signal: Callable = lambda: False, 
            link_failure: bool = True
        ) -> Callable:

        def target_function():
            return self.run(period, stop_signal=stop_signal, link_failure=link_failure)
        return target_function


    def thread(self, 
          period: float = 1.0, 
          stop_signal: Callable = lambda: False, 
          link_failure: bool = True
        ) -> Callable:
        return Thread( target = self.target_function(period, stop_signal, link_failure=link_failure) )
        
    def end(self):
        return self.monitor.end(self.device, self.data, None)
        

         
