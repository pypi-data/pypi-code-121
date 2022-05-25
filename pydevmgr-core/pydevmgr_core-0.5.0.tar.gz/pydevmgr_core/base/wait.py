from typing import Any, Callable, Dict, Iterable, Optional, Union
from .node import NodesReader, DictReadCollector, BaseNode
import time


class Waiter:   
    """ Object use to wait for some condition to be True 
    
    The only method of this object is :meth:`Waiter.wait`
    
    Args:
        node_or_func_list (iterable): an iterable of nodes or callable. Or a single node 
                    waiter.wait will wait until all node.get and callable return True (by default)
        logic (string, optional):
              "all_true"  : stop waiting when all check function return True (default)
              "all_false" : stop waiting when all check function return False
              "any_true"  : stop waiting when one of the check function return True
              "any_false" : stop waiting when one of the check function return False
            
        period : float, optional default is 0.1 second
            the sleep time in second in between checks
        timeout: float, optional second, default is 60
            if time since the call of the function exceed timeout an
            ValueError is raised.
            timeout is in second as well
        stop_signal (callable, optional): A callable object returning True to stop the wait. A stop signal will
                execute an optional stop_function and then raise a RuntimeError
                The example bellow is equivalent to setting a timeout. However timeout argument is kept for
                compatibility reason

                ::
                    
                    from pydevmgr_core.signals import Timeout 
                    from pydevmgr_core import wait 
                    wait( [... som stuff...], stop_signal=Timeout(60.0) )
        stop_function (callable, optional):  A callable to be executed in case of stop_signal 
        data (None, dict, optional):  If given input nodes values are taken from the 
               data dictionary which is expected to be updated in someother place.
        lag (float) : lag is a time in second corresponding to a sleep time before starting the wait process
                      This can be usefull to make sure that an action as started on the server before checking
                      the nodes
        
    Example:
        
    ::
        
        >>> wait_moving = Waiter([motor.stat.is_moving])
        >>> wait_moving.wait()
        
    wait return True and can be used as a trigger for a :class:`Download` object :
    
    :: 
    
        >>> data = {} 
        >>> pos_update = Downloader(data, [motor.stat.pos_actual], triger=wait_moving.wait)
        >>> t = Thread(target=pos_update.runner(0.5))
        >>> t.start()
        
    In the exemple above the thread will update the data dictionary 
    every 0.5 seconds with motor position only when the motor is moving. 
            
    Attributes:
        period (float): conditions are checks every period seconds
        timeout (float): timeout in second, a RuntimeError is raised if conditions
                         are still false after timeout.
    """
    def __init__(self, 
            node_or_func_list, 
            logic="all_true", 
            period=0.1,
            timeout=60,
            stop_signal = lambda: False,
            stop_function = lambda: None, 
            data=None,
            lag=0.0
          ) -> None:        
        
        nodes = []
        functions = []
        if not hasattr(node_or_func_list, "__iter__"): 
            node_or_func_list = [node_or_func_list]
        
        for f in node_or_func_list:
            if f is None: continue
            if isinstance(f, BaseNode):
                nodes.append(f)
            else:
                functions.append(f)
        
        self._functions = functions
            
        
        try:
            self.check_func, self.check_nodes = _logic_loockup[logic]
        except KeyError:
            raise ValueError("undefined logic %r must be one of %s"%(logic, ",".join(_logic_loockup.keys())))
        

        

        if data is None:
            reader = NodesReader(nodes)
        else:
            reader = DictReadCollector(data)
            for n in nodes:
                reader.add(n)           
        self.nodes = nodes               
        self.reader = reader    
        self.period  = period
        self.timeout = timeout
        self.stop_signal = stop_signal
        self.stop_function = stop_function
        self.lag = lag 
        
    def wait(self):
        """ run the wait condition """
        check_nodes     = self.check_nodes
        check_func     = self.check_func
        reader  = self.reader
        
        functions = self._functions         
        timeout   = self.timeout
        period    = self.period
        stop_signal = self.stop_signal
        
        s_time = time.time()
        if self.lag>0.0:
            time.sleep(self.lag)
        
        data_nodes = {}
        def check():
            # do the function first if it pass download the node values and check values 
            q = check_func(functions)
            if q:
                reader.read(data_nodes)
                return check_nodes( [data_nodes[n] for n in self.nodes] )
            return False
        
        # do the function first 
        while not check():
            if stop_signal():
                self.stop_function()
                raise RuntimeError(f"Wait interupted by stop_signal: {stop_signal}")
            if (time.time()-s_time)>timeout:
                raise RuntimeError('wait timeout')
            time.sleep(period)
        
        return True
    

def wait(
     node_or_func_list: Union[Iterable, BaseNode, Callable], 
     logic: str ="all_true", 
     period: float = 0.1, 
     timeout: float = 60, 
     stop_signal: Callable = lambda: False, 
     stop_function: Callable = lambda: None,  
     lag: float =0.0,  
     data: Optional[Dict[BaseNode, Any]]=None
    ) -> None:
    """ wait until a list of function return True

    Args:
        node_or_func_list (iterable): an iterable of nodes of callable.  Or a single node
                    wait will wait until all node.get and callable return True (by default)
                    
        logic (str, optional): 
              "all_true"  : stop waiting when all check function return True (default)
              "all_false" : stop waiting when all check function return False
              "any_true"  : stop waiting when one of the check function return True
              "any_false" : stop waiting when one of the check function return False
            
        period (float, optional): default is 0.1 second
            the sleep time in second in between checks
        timeout (float, optional): timeout in second, a RuntimeError is raised if conditions
                         are still false after timeout
        lag (float, optional): Add a flat time lag (in second) before checking nodes. 
                    This could be used to make sure that the last operation has been digested by server. 
                         
                    Bellow the lag is used to make sure that when ``wait`` starts the motor is moving
                          
                    ::
                             
                        >>> mgr.motor1.move_rel(1.0, 0.25)
                        >>> wait( [mgr.motor1.stat.is_standstill], lag=0.1 )
                        
        stop_signal (callable, optional): A callable object returning True to stop the wait. A stop signal will
                raise a RuntimeError
                The example bellow is equivalent to setting a timeout. However timeout argument is kept for
                compatibility reason

                ::
                    
                    from pydevmgr_core.signals import Timeout 
                    from pydevmgr_core import wait 
                    wait( [... som stuff...], stop_signal=Timeout(60.0) )
        stop_function (callable, optional): To be executed when a stop_signal is True

        data (None, dict, optional):  If given input nodes values are taken from the 
               data dictionary which is expected to be updated in someother place.

    Example:
        Wait until a motor initialised and an other custom function
        
        ::

            > def camera_ready():
            >   # <- do stuff ->
            >   return True # if camera is ready

            > wait( [motor.is_initialised, camera_ready] )

        Or something like
        
        ::
        
            > is_arrived = lambda : abs(motor.stat.pos_actual.get()-3.4)<0.01
            > wait( [is_arrived, camera_ready])

    """
    Waiter(node_or_func_list, logic=logic, period=period, timeout=timeout,  stop_signal = stop_signal, 
            stop_function = stop_function, data=data, lag=lag).wait()

def _all_true(functions):
    """ all_true(lst) -> return True if all function  list return True """
    for func in functions:
        if not func():
            return False
    return True

def _all_false(functions):
    """ all_false(lst) -> return True if all function in the list return False """

    for func in functions:
        if func():
            return False
    return True
    
def _any_true(functions):
    """ any_true(lst) -> return True if one of the function in the list return True """
    for func in functions:
        if func():
            return True        
    return False

def _any_false(functions):
    """ any_false(lst) -> return True if one of the function in the list return False """
    for func in functions:
        if not func():
            return True
    return False


""" Used in wait to define the logic applied """
_logic_loockup = {
    "all_true"  : (_all_true,  all),
    "all_false" : (_all_false, lambda l: not any(l) ), 
    "any_true"  : (_any_true,  any),
    "any_false" : (_any_false,  lambda l: not all(l))
}

