from typing import Dict,NamedTuple,Union
Blob=bytes
class ServiceKey(NamedTuple):
 account_id:str
 region:str
 service:str
Backends=Dict[str,Blob]
class BackendState:
 key:ServiceKey
 backends:Backends
 def __init__(self,key:ServiceKey,backends:Backends):
  self.key=key
  self.backends=backends
class ServiceState:
 state:Dict[ServiceKey,BackendState]
 def __init__(self):
  self.state={}
 def add(self,state_to_add:Union["ServiceState",BackendState]):
  if isinstance(state_to_add,self.__class__):
   self._merge_with_service(state_to_add)
  elif isinstance(state_to_add,BackendState):
   self._add_backend(state_to_add)
 def _add_backend(self,backend_state:BackendState):
  if backend_state.key not in self.state:
   self.state[backend_state.key]=backend_state
  else:
   from localstack_ext.bootstrap.pods.utils.merge_utils import get_merge_manager
   merge_manager=get_merge_manager(service=backend_state.key.service)
   if merge_manager:
    merge_manager.merge(a=self.state[backend_state.key].backends,b=backend_state.backends)
 def _merge_with_service(self,service:"ServiceState"):
  for backend in service.state.values():
   self._add_backend(backend)
 def is_empty(self)->bool:
  return len(self.state)==0
 def __str__(self)->str:
  return self.state.__str__()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
