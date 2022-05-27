from typing import Dict,NamedTuple,Union
Blob=bytes
class ServiceKey(NamedTuple):account_id:str;region:str;service:str
Backends=Dict[str,Blob]
class BackendState:
	key:0;backends:0
	def __init__(A,key,backends):A.key=key;A.backends=backends
class ServiceState:
	state:Dict[ServiceKey,BackendState];assets:Dict[str,Blob]
	def __init__(A):A.state={};A.assets={}
	def add(B,state_to_add):
		A=state_to_add
		if isinstance(A,B.__class__):B._merge_with_service(A)
		elif isinstance(A,BackendState):B._add_backend(A)
	def add_asset(A,service,content):A.assets[service]=content
	def _add_backend(B,backend_state):
		A=backend_state
		if A.key not in B.state:B.state[A.key]=A
		else:
			from localstack_ext.bootstrap.pods.utils.merge_utils import get_merge_manager as D;C=D(service=A.key.service)
			if C:C.merge(a=B.state[A.key].backends,b=A.backends)
	def _merge_with_service(B,service):
		A=service
		for C in A.state.values():B._add_backend(C)
		if A.assets:B._merge_assets(A.assets)
	def _merge_assets(A,assets):A.assets.update(assets)
	def is_empty(A):return len(A.state)==0
	def __str__(A):return f"Backends: {A.state.__str__()}\nAssets: {A.assets.__str__()}"