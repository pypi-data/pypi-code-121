# Builtin modules
from __future__ import annotations
import re, hmac
from hashlib import sha256
from time import time
from typing import Optional, Any, Union, List, Dict, Tuple
# Third party modules
from fsRPCClient import Client as _Client
from fsRPCClient.exceptions import InitializationError, ResponseError
from fsRPCClient.utils import hexToBytes
from fsLogger import Logger, T_Logger
from fsSignal import T_Signal
# Local modules
# Program
class Client(_Client):
	timeWindow:int
	path:str
	pubkey:bytes
	seckey:bytes
	def __init__(self, projectPublicKey:Optional[Union[str, bytes]]=None, projectSecretKey:Optional[Union[str, bytes]]=None,
	timeWindow:int=60, convertNumbers:Optional[str]=None, retryCount:int=10, retryDelay:Union[int, float]=5,
	connectTimeout:Union[int, float]=15, transferTimeout:Union[int, float]=320, disableCompression:bool=False,
	log:Optional[T_Logger]=None, signal:Optional[T_Signal]=None, target:Tuple[str, int]=("api.fusionexplorer.io", 443),
	httpHost:Optional[str]=None, ssl:bool=True) -> None:
		super().__init__(
			protocol           = "TCPv4:HTTP:JSONRPC-P",
			target             = target,
			connectTimeout     = connectTimeout,
			transferTimeout    = transferTimeout,
			retryCount         = retryCount,
			retryDelay         = retryDelay,
			ssl                = ssl,
			httpHost           = httpHost,
			disableCompression = disableCompression,
			useBulkRequest     = True,
			convertNumbers     = convertNumbers,
			log                = log or Logger("FusionExplorer"),
			signal             = signal,
		)
		self.timeWindow = timeWindow
		self.pubkey     = b""
		self.seckey     = b""
		if projectPublicKey is not None and len(projectPublicKey) > 0:
			if projectSecretKey is None:
				raise InitializationError("`projectSecretKey` is required when `projectPublicKey` is set")
			if isinstance(projectPublicKey, str):
				if not re.match(r'^(0x|)[0-9a-f]{32}$', projectPublicKey, re.I):
					raise InitializationError("`projectPublicKey` must be 32 character hex string")
				self.pubkey = hexToBytes(projectPublicKey)
			elif isinstance(projectPublicKey, bytes):
				self.pubkey = projectPublicKey
			else:
				raise InitializationError("`projectPublicKey` must be string or bytes")
			if len(self.pubkey) != 16:
				raise InitializationError("`projectPublicKey` must be 16 byte long")
			if isinstance(projectSecretKey, str):
				if not re.match(r'^(0x|)[0-9a-f]{32}$', projectSecretKey, re.I):
					raise InitializationError("`projectSecretKey` must be 32 character hex string")
				self.seckey = hexToBytes(projectSecretKey)
			elif isinstance(projectSecretKey, bytes):
				self.seckey = projectSecretKey
			else:
				raise InitializationError("`projectSecretKey` must be string or bytes")
			if len(self.seckey) != 16:
				raise InitializationError("`projectSecretKey` must be 16 byte long")
		self.log.debug("Public token: {}".format(self.pubkey.hex()))
		self.log.debug("Secret token: {}...{}".format(self.seckey[:1].hex(), self.seckey[-1:].hex()))
		self.log.info("Initialized")
	def __enter__(self) -> Client:
		return self
	def __exit__(self, type:Any, value:Any, traceback:Any) -> None:
		self.close()
	def __getstate__(self) -> Dict[str, Any]:
		r = super().__getstate__()
		r["pubkey"]     = self.pubkey
		r["seckey"]     = self.seckey
		r["timeWindow"] = self.timeWindow
		return r
	def __setstate__(self, states:Dict[str, Any]) -> None:
		super().__setstate__(states)
		self.pubkey     = states["pubkey"]
		self.seckey     = states["seckey"]
		self.timeWindow = states["timeWindow"]
	def _sendToSocket(self, payload:bytes, httpMethod:str="POST", path:str="/", httpHeaders:Dict[str, str]={}) -> None:
		if self.seckey:
			ts = int(time()+self.timeWindow).to_bytes(4, "big")
			httpHeaders["X-Auth"] = b"".join((
				ts,
				self.pubkey,
				hmac.digest(
					self.seckey,
					b"".join([
						ts,
						self.pubkey,
						sha256(payload).digest(),
					]),
					"SHA256"
				)
			)).hex()
		super()._sendToSocket(payload, httpMethod, path, httpHeaders)
	def clone(self, **kwargs:Any) -> Client:
		opts:Dict[str, Any] = {
			"projectPublicKey":  self.pubkey,
			"projectSecretKey":  self.seckey,
			"timeWindow":        self.timeWindow,
			"convertNumbers":    self.convertNumbers,
			"retryDelay":        self.retryDelay,
			"retryCount":        self.retryCount,
			"connectTimeout":    self.connectTimeout,
			"transferTimeout":   self.transferTimeout,
			"disableCompression":self.disableCompression,
			"log":               self.log,
			"signal":            self.signal,
			"target":            self.target,
			"httpHost":          self.httpHost,
			"ssl":               self.ssl,
		}
		opts.update(kwargs)
		return Client(**opts)
	def createIterator(self, method:str, *args:Any, sortBy:Optional[str]=None, fromKey:Optional[str]=None,
	desc:Optional[bool]=None, bitmask:Optional[int]=None, chunks:int=12) -> Any:
		if not method.startswith("iter"):
			raise InitializationError("For iterating you need choose method which name begins with `iter`.")
		kwargs:Dict[str, Any] = { "limit":chunks }
		if sortBy is not None: kwargs["sortBy"] = sortBy
		if fromKey is not None: kwargs["fromKey"] = fromKey
		if desc is not None: kwargs["desc"] = desc
		if bitmask is not None: kwargs["bitmask"] = bitmask
		return FEIterator(self.clone(), method, args, kwargs)

class FEIterator:
	def __init__(self, client:Any, method:str, args:Union[Tuple[Any, ...], List[Any]], kwargs:Dict[str, Any]) -> None:
		self.client = client
		self.method = method
		self.args = args
		self.kwargs = kwargs
		self.cache:List[Tuple[str, Any]] = []
	def __enter__(self) -> Any:
		return self
	def __exit__(self, type:Any, value:Any, traceback:Any) -> None:
		pass
	def __iter__(self) -> Any:
		return self
	def __request__(self) -> None:
		if not self.cache:
			req = self.client.request(self.method, self.args, self.kwargs)
			data = req.get()
			if not req.isSuccess():
				raise ResponseError(data)
			if type(data) is list:
				self.cache = [ (x["key"], x["data"]) for x in data ]
	def __next__(self) -> Tuple[Any, Any]:
		self.__request__()
		if not self.cache:
			raise StopIteration
		key, data = self.cache.pop(0)
		self.kwargs["fromKey"] = key
		return key, data
	def checkNext(self) -> Tuple[Any, Any]:
		self.__request__()
		if not self.cache:
			raise StopIteration
		return self.cache[0]
	def hasNext(self) -> bool:
		self.__request__()
		return bool(self.cache)
	next = __next__
