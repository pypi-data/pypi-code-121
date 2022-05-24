from typing import Dict,NamedTuple,Union
Blob=bytes
class ServiceKey(NamedTuple):account_id:str;region:str;service:str
Backends=Dict[str,Blob]
class BackendState:
	key:0;backends:0
	def __init__(A,key,backends):A.key=key;A.backends=backends
class ServiceState:
	state:Dict[ServiceKey,BackendState]
	def __init__(A):A.state={}
	def add(B,state_to_add):
		A=state_to_add
		if isinstance(A,B.__class__):B._merge_with_service(A)
		elif isinstance(A,BackendState):B._add_backend(A)
	def _add_backend(B,backend_state):
		A=backend_state
		if A.key not in B.state:B.state[A.key]=A
		else:
			from localstack_ext.bootstrap.pods.utils.merge_utils import get_merge_manager as D;C=D(service=A.key.service)
			if C:C.merge(a=B.state[A.key].backends,b=A.backends)
	def _merge_with_service(A,service):
		for B in service.state.values():A._add_backend(B)
	def is_empty(A):return len(A.state)==0
	def __str__(A):return A.state.__str__()