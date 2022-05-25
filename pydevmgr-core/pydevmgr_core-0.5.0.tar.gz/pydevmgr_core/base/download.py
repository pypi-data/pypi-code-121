from .node import NodesReader, BaseNode
from .base import  _BaseObject


import time
from collections import  OrderedDict

from typing import Any, Dict, Iterable, Union, Optional, Callable


class DataView:
    def __init__(self, 
            data: Dict[BaseNode,Any], 
            prefix: Optional[Union[str, _BaseObject]] = None
          ) -> None:
        self._data = data
        if prefix is None:
            prefix = ""
        if not isinstance(prefix, str):
            prefix = prefix.key 
        
        if not prefix:
            key_lookup = {n.key:n for n in data if hasattr(n, "key") }
        else:                    
            key_lookup = {}
            pref = prefix+"."
            lp = len(pref)
            for n in data:
                if hasattr(n, "key") and n.key.startswith(pref):
                    key_lookup[n.key[lp:]] = n
        
        self._key_lookup = key_lookup    
    
    def __repr__(self):
        return repr({k:self._data[n] for k,n in self._key_lookup.items() })
    
    def __str__(self):
        return str({k:self._data[n] for k,n in self._key_lookup.items() })
        
    def __getitem__(self, item):
        return self._data[self._key_lookup[item]]
    
    def __setitem__(self, item, value):
        self._data[self._key_lookup[item]] = value
    
    def __delitem__(self, item):
        del self._data[self._key_lookup[item]]
    
    def __getattr__(self, attr):
        return self._data[self._key_lookup[attr]]
    
    def __has__(self, item):
        return item in self._key_lookup
    
    def update(self, __d__={}, **kwargs) -> None:
        for k,v in dict(__d__, **kwargs).iteritems():
            self._data[self._key_lookup[k]] = v
    
    def pop(self, item) -> Any:
        """ Pop an item from the root data ! """
        return self._data.pop(self._key_lookup[item])    
    
    def popitem(self, item) -> Any:
        """ Pop an item from the root data ! """
        return self._data.popitem(self._key_lookup[item])  
    
    def keys(self) -> Iterable:
        """ D.keys() ->iterable on D's root keys with matching prefix
        
        Shall be avoided to use in a :class:`Prefixed` object
        """
        return self._key_lookup.__iter__()
    
    def items(self) -> Iterable:
        for k,n in self._key_lookup.items():
            yield k, self._data[n]
    
    def values(self) -> Iterable:
        for k,n in self._key_lookup.items():
            yield self._data[n]    
    
    def clear(self) -> None:
        """ D.clear() -> None.  Remove all items from D root with matching prefix
        
        Shall be avoided to use in a :class:`Prefixed` object
        """        
        pref = self._prefix+"."
        for k, n in list(self._key_lookup.items()):            
            self._data.pop(n)


def _setitem(d,k,v):
    d[k] = v
def _dummy_callback(data):
    pass
def _dummy_trigger():
    return True

class BaseDataLink:
    """ place holder for an instance check """    
    pass


class DownloaderConnection:
    """ Hold a connection to a :class:`Downloader` 
    
    Most likely created by :meth:`Downloader.new_connection` 
    
    Args:
       downloader (:class:`Downloader`) :  parent Downloader instance
       token (Any): Connection token 
    """
    def __init__(self, downloader, token):
        self._downloader = downloader 
        self._token = token 
    
    def _check_connection(self):
        if not self._token:
            raise RuntimeError("DownloaderConnection has been disconnected from its Downloader")
    
    @property
    def data(self) -> dict:
        """ downloader data """
        return self._downloader.data 
           
    def disconnect(self) -> None:
        """ disconnect connection from the downloader 
        
        All nodes related to this connection (and not used by other connection) are removed from the
        the downloader queue. 
        Also all callback associated with this connection will be removed from the downloader 
        
        Note that the disconnected nodes will stay inside the downloader data but will not be updated
        """
        self._downloader.disconnect(self._token)
        self._token = None
        
    def add_node(self, *nodes) -> None:
        """ Register nodes to be downloader associated to this connection 
        
        Args:
            *nodes :  nodes to be added to the download queue
        """ 
        self._check_connection() 
        self._downloader.add_node(self._token, *nodes)
    
    def add_nodes(self, nodes) -> None:
        """ Register nodes to be downloader associated to this connection 
        
        Args:
            nodes :  nodes to be added to the download queue. 
                     If a dictionary of node/value pairs, they are added to the downloader data. 
        """
        self._check_connection() 
        self._downloader.add_nodes(self._token, nodes)
    
    def remove_node(self, *nodes) -> None:
        """ remove  any nodes to the downloader associated to this connection 
        
        Note that the node will stay inside the downloader data but will not be updated 
        
        Args:
            *nodes :  nodes to be removed from the download queue
        """ 
        self._check_connection() 
        self._downloader.remove_node(self._token, *nodes)
    
    def add_datalink(self, *datalinks) -> None:
        """ Register datalinks to the downloader associated to this connection 
        
        Args:
            *datalinks :  :class:`DataLink` to be added to the download queue on the associated downloader
        """
        self._check_connection() 
        self._downloader.add_datalink(self._token, *datalinks)        
    
    def remove_datalink(self, *datalinks) -> None:
        """ Remove any given datalinks to the downloader associated to this connection 
        
        Args:
            *datalinks :  :class:`DataLink` to be removed 
        """
        self._check_connection() 
        self._downloader.remove_datalink(self._token, *datalinks)        
    
    def add_callback(self, *callbacks) -> None:
        """ Register callbacks to be executed after each download of the associated downloader 
        
        Args:            
            *callbacks :  callbacks to be added to the queue of callbacks on the associated downloader       
        """
        self._check_connection() 
        self._downloader.add_callback(self._token, *callbacks)
    
    def remove_callback(self, *callbacks) -> None:
        """ Remove any of given callbacks of the associated downloader 
        
        Args:            
            *callbacks :  callbacks to be remove 
        """
        self._check_connection() 
        self._downloader.remove_callback(self._token, *callbacks)
    
    def add_failure_callback(self, *callbacks) -> None:
        """ Register callbacks to be executed after each download of the associated downloader 
        
        Args:            
            *callbacks :  failure callbacks to be added to the queue of callbacks on the associated downloader       
        """
        self._check_connection() 
        self._downloader.add_failure_callback(self._token, *callbacks)
        
    def remove_failure_callback(self, *callbacks) -> None:
        """ Remove any given callbacks of the associated downloader 
        
        Args:            
            *callbacks :  failure callbacks to be removed 
        """
        self._check_connection() 
        self._downloader.remove_failure_callback(self._token, *callbacks)

class StopDownloader(StopIteration):
    pass

class Downloader:
    """ object dedicated to download nodes, feed data and run some callback 

    An application can request nodes to be downloaded and callback to be executed after each 
    success download or each failures. 
    
    Args:    
        nodes_or_datalink (iterable of node or :class:`DataLink`): 
            - An initial, always downloaded, list of nodes 
            - Or a :class:`DataLink` object
        data (dict, optional): A dictionary to store the data. If not given, one is created and
                               accessible through the .data attribute. 
                               This data is made of node/value pairs, the .get_data_view gives however
                               a dictionary like object with string/value pairs. 
                               Each time a new node is added to the downloader it will be added to 
                               the data as ``data[node] = None``. None will be replaced after the 
                               next download.  
                               
        callback (callable, optional): one single function with signature f(), if given always 
                                      called after successful download. 
        trigger (callable, optional): a function taking no argument and should return True or False 
                                      If given the "download" method download nodes only if f() return True. 
                                      Can be used if the download object is running in a thread for instance.
    
    Example: 
    
        A dumy exemple, replace the print_pos by a GUI interface for instance:
        
        ::
                        
            def print_pos(m, data):
                "An application"
                print("Position :",  data[m.stat.pos_actual], data[m.stat.pos_error] )
                
            >>> tins = open_manager('tins/tins.yml')
            >>> tins.connect() 
            >>> downloader = Downloader()
            >>> token = downloader.new_token()
            >>> downloader.add_node(token, tins.motor1.stat.pos_actual, tins.motor1.stat.pos_error )
            >>> downloader.add_callback(token, lambda : print_pos(tins.motor1, downloader.data))
            >>> downloader.download() 
            Position : 3.45 0.003
            >>> downloader.data
            {
            <UaNode key='motor1.pos_error'>: 0.003, 
            <UaNode key='motor1.pos_actual'>:  3.45
            }
            
            >>> downloader.disconnect(token) # disconnect the print_pos function and remove 
                                             # the pos_actual, pos_error node from the list of nodes
                                             # to download (except if an other connection use it)
            
        Same result can be obtained with this exemple: 
        
        :: 
        
            def print_pos(data):
                "An application"
                print("Position :",  data['pos_actual'], data['pos_error'] )
            
            >>> nodes_data = {tins.motor1.stat.pos_actual: -9.99 , tins.motor1.stat.pos_error: -9.99}
            >>> m1_data = DataView(nodes_data, tins.motor1.stat)            
            >>> downloader = Downloader(nodes_data, callback=lambda: print_pos(m1_data))
            >>> downloader.download() 
            Position : 3.45 0.003
            >>> m1_data
            {'pos_error': 0.003, 'pos_actual': 3.45}
        
        
        
                                     
    """
    
    _did_failed_flag = False 
    Connection = DownloaderConnection
    StopDownloader = StopDownloader
    
    def __init__(self,  
            nodes_or_datalink: Union[Iterable, BaseDataLink] = None,  
            data: Optional[Dict] = None, 
            callback: Optional[Callable] = None,
            trigger: Optional[Callable] = None
        ) -> None:
        if data is None:
            data = {}
               
        self._data = data 
        
        if nodes_or_datalink is None:
            nodes = set()
            datalinks = set()
        elif isinstance(nodes_or_datalink, BaseDataLink):
            nodes = set()
            datalinks = set([nodes_or_datalink])
        
        elif isinstance( nodes_or_datalink, dict):
            nodes = set()
            datalinks = set()
            for k,v in nodes_or_datalink.items():
                if isinstance( v, BaseDataLink ):
                    datalinks.add(v)
                else:
                    nodes.add(v)
        
        else:
            nodes = set()
            datalinks = set()
            for v in nodes_or_datalink:
                if isinstance( v, BaseDataLink ):
                    datalinks.add(v)
                else:
                    nodes.add(v)
            



        #nodes = set() if nodes is None else set(nodes)
        if callback is None:
            callbacks = set()
        else:
            callbacks = set([callback])
            
        failure_callbacks = set() 
        
        if callback is None:
            callback = _dummy_callback
        if trigger is None:
            trigger =  _dummy_trigger
        
        self._trigger = trigger
        # Ellipsis is here to define general nodes,datalinks,callbacks, ... independent to connection
        self._dict_nodes = OrderedDict([(Ellipsis,nodes)])
        self._dict_datalinks = OrderedDict([(Ellipsis,datalinks)])
        self._dict_callbacks = OrderedDict([(Ellipsis,callbacks)])
        self._dict_failure_callbacks = OrderedDict([(Ellipsis,failure_callbacks)])
        
        
        self.trigger = trigger
        self._next_token = 1
        
        self._rebuild_nodes()
        self._rebuild_callbacks()
        self._rebuild_failure_callbacks()
    
    def __has__(self, node):
        return node in self._nodes
    
    @property
    def data(self):
        return self._data
    
    def _rebuild_nodes(self):
        nodes = set()
        for nds in self._dict_nodes.values():
            nodes.update(nds)
            for n in nds:
                self._data.setdefault(n,None)
        for dls in self._dict_datalinks.values():
            for dl in dls:
                nodes.update(dl.rnodes)
                for n in dl.rnodes:
                    self._data.setdefault(n,None)
                
        self._nodes = nodes
        self._to_read = NodesReader(nodes)

    def _rebuild_callbacks(self):
        callbacks = set()
        for clbc in self._dict_callbacks.values():
            callbacks.update(clbc)
        self._callbacks = callbacks
    
    def _rebuild_failure_callbacks(self):
        callbacks = set()
        for clbc in self._dict_failure_callbacks.values():
            callbacks.update(clbc)
        self._failure_callbacks = callbacks
    
    
    def new_token(self) -> tuple:
        """ add a new app connection token
        
        Return:
           A token, the token and type itself is not relevant, it is just a unique ID to be used in 
                    add_node, add_callback, add_failure_callback, and disconnect methods 
                    
        .. note::
        
            new_connection() method return object containing a pair of token and downloader and all
                methods necessary to add_nodes, add_callbacks, etc ... 
                
        
        """
        token = id(self), self._next_token
        self._dict_nodes[token] = set()
        self._dict_datalinks[token] = set()
        self._dict_callbacks[token] = set()
        self._dict_failure_callbacks[token] = set()
        
        self._next_token += 1
        # self._rebuild_nodes()
        # self._rebuild_callbacks()
        # self._rebuild_failure_callbacks()
        return token
    
    def new_connection(self):
        """ Return a :class:`DownloaderConnection` object 
        
        The :class:`DownloaderConnection` object contain a token and the downloader in order to have 
        a standalone object to handle the add/remove of queue nodes and callbacks 
        """
        return DownloaderConnection(self, self.new_token())
    
    def disconnect(self, token: tuple) -> None:
        """ Disconnect the iddentified connection 
        
        All the nodes used by the connection (and not by other connected app) will be removed from the 
        download queue of nodes.
        Also all callback associated with this connection will be removed from the downloader 
        
        Note that the discnnected nodes will stay inside the downloader data but will not be updated
         
        Args:
            token : a Token returned by :func:`Downloader.new_token`
        """
        if token is Ellipsis:
            raise ValueError('please provide a real token')
        
        try:
            self._dict_nodes.pop(token)
            self._dict_datalinks.pop(token)
            self._dict_callbacks.pop(token)
            self._dict_failure_callbacks.pop(token)
        except KeyError:
            pass
        
        self._rebuild_nodes()
        self._rebuild_callbacks()
        self._rebuild_failure_callbacks()
    
    def add_node(self, token: tuple, *nodes) -> None:
        """ Register node to be downloaded for an iddentified app
        
        Args:
            token: a Token returned by :func:`Downloader.new_token` 
                   ``add_node(...,node1, node2)`` can also be used, in this case nodes will be added
                   to the main pool of nodes and cannot be removed from the downloader 
            *nodes :  nodes to be added to the download queue, associated to the app
        """   
        self._dict_nodes[token].update(nodes)
        self._rebuild_nodes()
    
    def add_nodes(self, token: tuple, nodes: Union[dict,Iterable]) -> None:
        """ Register nodes to be downloaded for an iddentified app
        
        Args:
            token: a Token returned by :func:`Downloader.new_token` 
                   ``add_node(...,node1, node2)`` can also be used, in this case nodes will be added
                   to the main pool of nodes and cannot be removed from the downloader 
            nodes (Iterable, dict):  nodes to be added to the download queue, associated to the app
                   If a dictionary of node/value pairs, they are added to the downloader data.  
        """
        if isinstance(nodes, dict):
            for node,val in nodes.items():
                self._data[node] = val
        
        self._dict_nodes[token].update(nodes)
        self._rebuild_nodes()
    
    def remove_node(self, token: tuple, *nodes) -> None:
        """ Remove node from the download queue
    
        if the node is not in the queueu nothing is done or raised
        
        Note that the node will stay inside the downloader data but will not be updated 
        
        Args:
            token: a Token returned by :func:`Downloader.new_token`                  
            *nodes :  nodes to be removed 
        """   
        for node in nodes:
            try:
                self._dict_nodes[token].remove(node)
            except KeyError:
                pass 
        self._rebuild_nodes()
    
    def add_datalink(self, token: tuple, *datalinks) -> None:
        """ Register a new datalink
        
        Args:
            token: a Token returned by :func:`Downloader.new_token`
                ``add_datalink(...,dl1, dl2)`` can also be used, in this case they will be added
                to the main pool of datalinks and cannot be remove from the downloader   
            *datalinks :  :class:`DataLink` to be added to the download queue, associated to the token 
        """           
        self._dict_datalinks[token].update(datalinks)
        self._rebuild_nodes()    
    
    def remove_datalink(self, token: tuple, *datalinks) -> None:
        """ Remove a datalink from a established connection
        
        If the datalink is not in the queueu nothing is done or raised
        
        Args:
            token: a Token returned by :func:`Downloader.new_token`
            *datalinks :  :class:`DataLink` objects to be removed         
        """
        for dl in  datalinks:
            try:
                self._dict_datalinks[token].remove(dl)
            except KeyError:
                pass 
        self._rebuild_nodes()
        
    def add_callback(self, token: tuple, *callbacks) -> None:   
        """ Register callbacks to be executed after each download 
        
        The callback must have the signature f(), no arguments.
        
        Args:
            token: a Token returned by :func:`Downloader.new_connection`
            *callbacks :  callbacks to be added to the queue of callbacks, associated to the app
        
        """ 
        self._dict_callbacks[token].update(callbacks)
        self._rebuild_callbacks()
    
    def remove_callback(self, token: tuple, *callbacks) -> None:   
        """ Remove callbacks 
        
        If the callback  is not in the queueu nothing is done or raised
        
        Args:
            token: a Token returned by :func:`Downloader.new_token`
            *callbacks :  callbacks to be removed 
        
        """
        for c in callbacks:
            try:
                self._dict_callbacks[token].remove(c)
            except KeyError:
                pass 
        self._rebuild_callbacks()
    
    
    def add_failure_callback(self, token: tuple, *callbacks) -> None:  
        """ Add one or several callbacks to be executed when a download failed 
        
        When ever occur a failure (Exception during download) ``f(e)`` is called with ``e`` the exception. 
        If a download is successfull after a failure ``f(None)`` is called one time only.
                
        Args:
            token: a Token returned by :func:`Downloader.new_token`
            *callbacks: callbacks to be added to the queue of failure callbacks, associated to the app
        
        """ 
        self._dict_failure_callbacks[token].update(callbacks)
        self._rebuild_failure_callbacks()
    
    def remove_failure_callback(self, token: tuple, *callbacks) -> None:  
        """ remove  one or several failure callbacks 
        
        If the callback  is not in the queue nothing is done or raised
        
        Args:
            token: a Token returned by :func:`Downloader.new_token`
            *callbacks :  callbacks to be removed         
        """ 
        for c in callbacks:
            try:
                self._dict_failure_callbacks[token].remove(c)
            except KeyError:
                pass         
        self._rebuild_failure_callbacks()
    
    
    def run(self, 
            period: float =1.0, 
            stop_signal: Callable =lambda : False, 
            sleepfunc: Callable =time.sleep
        ) -> None:
        """ run the download indefinitely or when stop_signal return True 
        
        Args:
            period (float, optional): period between downloads in second
            stop_signal (callable, optional): a function returning True to stop the loop or False to continue
            
        """
        try:
            while not stop_signal():
                s_time = time.time()
                self.download()
                sleepfunc( max( period-(time.time()-s_time), 0))
        except StopDownloader: # any downloader call back can send a StopDownloader to stop the runner 
            return 
            
    def runner(self, 
        period: float =1.0, 
        stop_signal: Callable =lambda : False, 
        sleepfunc: Callable =time.sleep
        ) -> Callable: 
        """ Create a function to run the download in a loop 
        
        Usefull to define a Thread for instance
        
        Args:
            period (float, optional): period between downloads in second
            stop_signal (callable, optional): a function returning True to stop the loop or False to continue
        
        Example:
            
            >>> downloader = Downloader([mgr.motor1.substate, mgr.motor1.pos_actual])
            >>> t = Thread( target = downloader.runner(period=0.1) )
            >>> t.start()
            
        """       
        def run_func():
            self.run(period=period, sleepfunc=sleepfunc, stop_signal=stop_signal)
        return run_func
    
    def download(self) -> None:
        """ Execute a download 
        
        Each nodes on the queue are fetched and the .data dictionary is updated
        from new values.
        
        If the Downloader has a trigger method and the trigger return false, nothing is done
        
        """
        
        if not self.trigger(): return 
        
        try:
            self._to_read.read(self._data)
        except Exception as e:
            if self._failure_callbacks:
                self._did_failed_flag = True
                for func in self._failure_callbacks:                    
                    func(e)
            else:
                raise e            
        else:
            # Populate the data links 
            for dls in self._dict_datalinks.values():
                for dl in dls:
                    dl._download_from(self._data)
            
            if self._did_failed_flag:
                self._did_failed_flag = False
                for func in self._failure_callbacks:                    
                    func(None)
                    
            for func in self._callbacks:
                func()
    
    def reset(self) -> None:
        """ All nodes of the downloader with a reset method will be reseted """
        reset(self._dict_nodes)
            
    def get_data_view(self, prefix: str ='') -> DataView:
        """ Return a view of the data in a dictionary where keys are string keys extracted from nodes
        
        If prefix is given the return object will be limited to items with key
        matching the prefix.  
        
        Note: the data view reflect any change made on the rootdata except when new nodes 
        (mathing the prefix) are added. So all necessary nodes shall be added to the downloader 
        before requesting a DataView. 
        
        Args:
           prefix (str, optional): limit the data viewer to a given prefix. prefix can also be an object 
                                with the key attribute like a :class:`BaseDevice`, :class:`BaseNode` etc ...
        
        Example:
            
            ::
                
                > downloader = Downloader([mgr.motor1.substate, mgr.motor1.pos_actual, mgr.motor2.substate])
                > downloader.download()
                > m1_data = downloader.get_data_view(mgr.motor1.key) 
                > m1_data['pos_actual']
                3.9898
            
            ::
            
                > m1_data = downloader.get_data_view(mgr.motor1)
                # is equivalent to 
                > m1_data = DataView(downloader.data, mgr.motor1)
        """
        return DataView(self._data, prefix)        
    
    def clean_data(self) -> None:
        """ Remove to the .data dictionary all keys/value pairs corresponding to nodes not in the downloader queue
        
        Returns:
           n (int): The number of node/value pair removed 
        """
        d = self.data
        n = 0
        for n in list(d): # list(d) in order to avoid deletion on the iterator
            if not n in self._nodes:
                d.pop(n, None)
                n+=1
        return n


def reset(nodes: Iterable):
    """ Execute the reset() method of a list of nodes """
    for n in nodes:
        n.reset()

def download(nodes, data: Optional[Dict] = None) -> Union[list,None]:
    """ read node values from remote servers in one call per server    

    Args:
        nodes (iterable):
             Iterable of nodes, like [mgr.motor1.stat.pos_actual, mgr.motor2.stat.pos_actual]
        
        data (dict, optional):
             This is mostlikely a dictionary, must define a __setitem__ method
             If given the function return None and update data in place. 
             If data is None the function return a list of values 
             
        
    Returns:
       None, or list : download(nodes) -> return list of values 
                       download(nodes, data) -> return None and update the input data dictionary
    
    Example:
    
    ::
        
        data = {n:n.get() for n in nodes}
    
    Is equivalent, but **much slower** than 
    
    :: 
        
        data = {}
        download(nodes)
        
    The latest is more efficient because only one call (per server) is done.
    
    data dictionary is optional, if not given values are returned in a list:
    
    ::
     
        pos, error = download([mgr.motor1.stat.pos_actual, mgr.motor1.stat.pos_error])
     
    
    """
    if data is None:
        data = {}
        nodes = tuple(nodes) # in case this is a generator  
        NodesReader(nodes).read(data)
        return [data[n] for n in nodes]
    else:    
        NodesReader(nodes).read(data)
        return None


