# Builtin modules
from __future__ import annotations
from time import monotonic
from typing import Any, Union, List, Dict, Optional
# Third party modules
# Local modules
from .abcs import T_Request, T_Client, NoPayload
# Program
class Request(T_Request):
	def __init__(self, client:T_Client, id:Any, method:str, args:List[Any], kwargs:Dict[str, Any], path:str="/",
	httpMethod:str="POST", httpHeaders:Dict[str, str]={}, payload:Any=NoPayload,
	convertNumbers:Optional[str]=None) -> None:
		self._client         = client
		self._id             = id
		self._method         = method
		self._args           = args
		self._kwargs         = kwargs
		self._path           = path
		self._httpMethod     = httpMethod
		self._httpHeaders    = httpHeaders
		self._payload        = payload
		self._convertNumbers = convertNumbers
		#
		self._requestTime  = monotonic()
		self._responseTime = 0.0
		self._uid          = ""
		self._done         = False
		self._success      = False
		self._response     = None
	def _get(self) -> None:
		self._client._get(self._id)
		return None
	def _parseResponse(self, id:Union[int, str], isSuccess:bool, result:Any, uid:str) -> None:
		self._done = True
		self._responseTime = monotonic()
		self._uid = uid
		self._success = isSuccess
		self._response = result
	def _dumps(self) -> Any:
		r:Any
		if self._client.requestProtocol == "JSONRPC-2":
			r = {
				"jsonrpc":"2.0",
				"params":self._kwargs or self._args,
				"method":self._method,
				"id":self._id,
			}
			if self._convertNumbers is not None:
				r["convertNumbers"] = self._convertNumbers
		elif self._client.requestProtocol == "JSONRPC-P":
			r = {
				"jsonrpc":"python",
				"args":self._args,
				"kwargs":self._kwargs,
				"method":self._method,
				"id":self._id,
			}
			if self._convertNumbers is not None:
				r["convertNumbers"] = self._convertNumbers
		elif self._client.requestProtocol in ("REST", "RAW"):
			r = self._payload
		elif self._client.requestProtocol == "FSP":
			r = (self._id, self._method, self._args, self._kwargs)
		elif self._client.requestProtocol == "OldFSProtocol":
			r = (self._id, self._method, self._args, self._kwargs)
		else:
			raise RuntimeError
		return r
	def get(self) -> Any:
		if not self._done:
			self._get()
		return self._response
	def getDelay(self) -> float:
		if not self._done:
			self._get()
		return self._responseTime - self._requestTime
	def getID(self) -> Any:
		return self._id
	def isDone(self) -> bool:
		return self._done
	def getUID(self) -> str:
		if not self._done:
			self._get()
		return self._uid
	def isSuccess(self) -> bool:
		if not self._done:
			self._get()
		return self._success
