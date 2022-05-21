# Builtin modules
from __future__ import annotations
import json, weakref, pickle
from lz4.frame import decompress # type: ignore
from typing import Any, Union, List, Dict, Tuple, Optional, Callable, cast
# Third party modules
import fsPacker
from fsLogger import Logger, T_Logger
from fsSignal import HardSignal, KillSignal, T_Signal
# Local modules
from .exceptions import InitializationError, RequestError, ResponseError, BaseRPCError
from .utils import iterSplit
from .clientSocket import HTTPClientSocket, StringClientSocket, FSPackerClientSocket, OldFSProtocolClientSocket
from .abcs import (T_Request, T_Client, T_Headers, T_HTTPClientSocket, T_BaseClientSocket_send_default, T_SocketBindAddress,
T_BaseClientSocket_send_http, T_StringClientSocket, T_FSPackerClientSocket, T_OldFSPackerClientSocket, NoPayload)
from .requestObj import Request
# Program
_dumpRequest:Callable[[T_Request], Any] = lambda x: x._dumps()

class Client(T_Client):
	max_bulk_request:int = 0xFF
	FSPACKER_VERSION:int = fsPacker.HIGHEST_VERSION
	def __init__(self, protocol:str, target:Union[str, Tuple[str, int], Tuple[str, int, int, int]],
	connectTimeout:Union[int, float]=15, transferTimeout:Union[int, float]=320, retryCount:int=10,
	retryDelay:Union[int, float]=5, ssl:bool=False, sslHostname:Optional[str]=None, httpHost:Optional[str]=None,
	extraHttpHeaders:Dict[str, str]={}, disableCompression:bool=False, useBulkRequest:bool=True,
	convertNumbers:Optional[str]=None, bind:Optional[T_SocketBindAddress]=None, log:Optional[T_Logger]=None,
	signal:Optional[T_Signal]=None) -> None:
		self.protocol           = protocol
		self.target             = target
		self.connectTimeout     = float(connectTimeout)
		self.transferTimeout    = float(transferTimeout)
		self.retryCount         = retryCount
		self.retryDelay         = float(retryDelay)
		self.ssl                = ssl
		self.sslHostname        = sslHostname
		self.httpHost           = httpHost
		self.extraHttpHeaders   = extraHttpHeaders
		self.disableCompression = disableCompression
		self.useBulkRequest     = useBulkRequest
		self.convertNumbers     = convertNumbers
		self.bind               = bind
		self.log                = log or Logger("RPCClient")
		self.signal             = signal or HardSignal()
		self.id                 = 0
		self.requests           = weakref.WeakValueDictionary()
		self.socketErrors       = 0
		if self.connectTimeout < 0:
			raise InitializationError("`connectTimeout` must be greater than 0")
		if self.transferTimeout < 0:
			raise InitializationError("`transferTimeout` must be greater than 0")
		if self.retryCount < 0:
			raise InitializationError("`retryCount` must be positive integer")
		if self.retryDelay < 0:
			raise InitializationError("`retryDelay` must be greater or equal than 0")
		if self.convertNumbers is not None and self.convertNumbers not in ["default", "none", "hex", "str"]:
			raise InitializationError("When `convertNumbers` is set, then most be the following one: default, none, hex or str")
		self._initializeProtocol()
	def _initializeProtocol(self) -> None:
		if ":" not in self.protocol:
			raise InitializationError("Invalid protocol")
		protocolParts = self.protocol.split(":")
		if len(protocolParts) != 3:
			raise InitializationError("Invalid protocol")
		self.socketProtocol, self.messageProtocol, self.requestProtocol = protocolParts
		if self.socketProtocol == "IPC":
			self.target = cast(str, self.target)
			if not isinstance(self.target, str):
				raise InitializationError("Target must be path")
		elif self.socketProtocol == "TCPv4":
			self.target = cast(Tuple[str, int], self.target)
			if not isinstance(self.target, (tuple, list)) or len(self.target) != 2 or \
			not isinstance(self.target[0], str) or not isinstance(self.target[1], int):
				raise InitializationError("Target must be address and port in a list or tuple")
		elif self.socketProtocol == "TCPv6":
			self.target = cast(Tuple[str, int, int, int], self.target)
			if  not isinstance(self.target, (tuple, list)) or len(self.target) != 4 or \
			not isinstance(self.target[0], str) or not isinstance(self.target[1], int) or \
			not isinstance(self.target[2], int) or not isinstance(self.target[3], int):
				raise InitializationError("Target must be address, port, flow info and scope id in a list or tuple")
		else:
			raise InitializationError("Unsupported socket protocol")
		if self.messageProtocol not in ["HTTP", "STR", "FSP", "OldFSProtocol"]:
			raise InitializationError("Unsupported message protocol")
		if self.requestProtocol in ("REST", "RAW"):
			self.useBulkRequest = False
		elif self.requestProtocol not in ("JSONRPC-2", "JSONRPC-P", "FSP", "OldFSProtocol"):
			raise InitializationError("Unsupported request protocol")
		if self.messageProtocol == "OldFSProtocol":
			if self.requestProtocol != "OldFSProtocol":
				raise InitializationError("Unsupported request protocol")
			self.useBulkRequest = False
		if self.log.isFiltered("TRACE"):
			self.log.debug(
				"Protocol initialized  [sockProt: {}][msgProt: {}][reqProt: {}][target: {}][SSL: {}]",
				self.socketProtocol, self.messageProtocol, self.requestProtocol, self.target, self.ssl
			)
		elif self.log.isFiltered("DEBUG"):
			self.log.debug("Protocol initialized")
	def __enter__(self) -> T_Client:
		return self
	def __exit__(self, type:Any, value:Any, traceback:Any) -> None:
		self.close()
	def __getstate__(self) -> Dict[str, Any]:
		return {
			"target":            self.target,
			"protocol":          self.protocol,
			"connectTimeout":    self.connectTimeout,
			"transferTimeout":   self.transferTimeout,
			"retryCount":        self.retryCount,
			"retryDelay":        self.retryDelay,
			"ssl":               self.ssl,
			"sslHostname":       self.sslHostname,
			"httpHost":          self.httpHost,
			"extraHttpHeaders":  self.extraHttpHeaders,
			"disableCompression":self.disableCompression,
			"useBulkRequest":    self.useBulkRequest,
			"convertNumbers":    self.convertNumbers,
			"bind":              self.bind,
			"log":               self.log,
			"signal":            self.signal,
		}
	def __setstate__(self, states:Dict[str, Any]) -> None:
		self.target             = states["target"]
		self.protocol           = states["protocol"]
		self.connectTimeout     = states["connectTimeout"]
		self.transferTimeout    = states["transferTimeout"]
		self.retryCount         = states["retryCount"]
		self.retryDelay         = states["retryDelay"]
		self.ssl                = states["ssl"]
		self.sslHostname        = states["sslHostname"]
		self.httpHost           = states["httpHost"]
		self.extraHttpHeaders   = states["extraHttpHeaders"]
		self.disableCompression = states["disableCompression"]
		self.useBulkRequest     = states["useBulkRequest"]
		self.convertNumbers     = states["convertNumbers"]
		self.bind               = states["bind"]
		self.log                = states["log"]
		self.signal             = states["signal"]
		self.id                 = 0
		self.requests           = weakref.WeakValueDictionary()
	def _connect(self, sendOlderRequests:bool=True) -> None:
		self.socket.connect()
		self.log.info("Connected")
		if sendOlderRequests:
			objs:List[T_Request] = list(filter(lambda x: not x.isDone(), self.requests.values()))
			if objs:
				objs.sort(key=lambda x: x._requestTime)
				self.log.info("Sending {} previous requests", len(objs))
				chunkToSend:Any
				if self.useBulkRequest and len(objs) > 1:
					for chunk in iterSplit(list(map(_dumpRequest, objs)), self.max_bulk_request):
						self._sendRequest(chunk)
				else:
					for obj in objs:
						self._sendRequest(obj._dumps(), obj._httpMethod, obj._path, obj._httpHeaders)
	def _sendRequest(self, data:Any, httpMethod:str="POST", path:str="/", httpHeaders:Dict[str, str]={}) -> None:
		payload:bytes = b""
		if isinstance(self.socket, T_HTTPClientSocket):
			if "host" not in httpHeaders:
				httpHeaders["host"] = self.httpHost or "{}:{}".format(self.target[0], self.target[1])
			if data is not NoPayload:
				if self.requestProtocol in ["JSONRPC-2", "JSONRPC-P", "REST"]:
					if "content-type" not in httpHeaders:
						httpHeaders["content-type"] = "application/json;charset=utf-8"
					payload = json.dumps(data).encode('utf8')
				elif self.requestProtocol == "FSP":
					if "content-type" not in httpHeaders:
						httpHeaders["content-type"] = "application/fspacker"
					payload = fsPacker.dumps(data, version=self.FSPACKER_VERSION)
				elif self.requestProtocol == "RAW":
					assert type(data) is bytes
					payload = data
				else:
					raise RuntimeError
			self._sendToSocket(payload, httpMethod, path, httpHeaders)
		elif isinstance(self.socket, T_FSPackerClientSocket):
			if self.requestProtocol in ["JSONRPC-2", "JSONRPC-P", "REST"]:
				payload = json.dumps(data).encode('utf8')
			elif self.requestProtocol == "FSP":
				payload = fsPacker.dumps(data, version=self.FSPACKER_VERSION)
			elif self.requestProtocol == "RAW":
				assert type(data) is bytes
				payload = data
			else:
				raise RuntimeError
			self._sendToSocket(payload)
		elif isinstance(self.socket, T_OldFSPackerClientSocket):
			if self.requestProtocol == "OldFSProtocol":
				payload = pickle.dumps(data)
			else:
				raise RuntimeError
			self._sendToSocket(payload)
		elif isinstance(self.socket, T_StringClientSocket):
			if self.requestProtocol in ["JSONRPC-2", "JSONRPC-P", "REST"]:
				payload = json.dumps(data).encode('utf8')
			elif self.requestProtocol == "FSP":
				payload = fsPacker.dumps(data, version=self.FSPACKER_VERSION).hex().encode('utf8')
			elif self.requestProtocol == "RAW":
				if type(data) is bytes:
					payload = data
				else:
					payload = data.encode("utf8")
			else:
				raise RuntimeError
			self._sendToSocket(payload)
		else:
			raise RuntimeError
	def _sendToSocket(self, payload:bytes, httpMethod:str="POST", path:str="/", httpHeaders:Dict[str, str]={}) -> None:
		if isinstance(self.socket, T_BaseClientSocket_send_http):
			self.socket.send(payload, httpMethod, path, httpHeaders)
		elif isinstance(self.socket, T_BaseClientSocket_send_default):
			self.socket.send(payload)
		else:
			raise RuntimeError
	def _createSocket(self) -> None:
		if not hasattr(self, "socket"):
			if self.messageProtocol == "HTTP":
				self.socket = HTTPClientSocket(
					client             = self,
					protocol           = self.socketProtocol,
					target             = self.target,
					bind               = self.bind,
					connectTimeout     = self.connectTimeout,
					transferTimeout    = self.transferTimeout,
					ssl                = self.ssl,
					sslHostname        = self.sslHostname,
					extraHeaders       = self.extraHttpHeaders,
					disableCompression = self.disableCompression,
				)
			elif self.messageProtocol == "STR":
				self.socket = StringClientSocket(
					client          = self,
					protocol        = self.socketProtocol,
					target          = self.target,
					bind            = self.bind,
					connectTimeout  = self.connectTimeout,
					transferTimeout = self.transferTimeout,
					ssl             = False,
					sslHostname     = None,
				)
			elif self.messageProtocol == "FSP":
				self.socket = FSPackerClientSocket(
					client          = self,
					protocol        = self.socketProtocol,
					target          = self.target,
					bind            = self.bind,
					connectTimeout  = self.connectTimeout,
					transferTimeout = self.transferTimeout,
					ssl             = False,
					sslHostname     = None,
				)
			elif self.messageProtocol == "OldFSProtocol":
				self.socket = OldFSProtocolClientSocket(
					client          = self,
					protocol        = self.socketProtocol,
					target          = self.target,
					bind            = self.bind,
					connectTimeout  = self.connectTimeout,
					transferTimeout = self.transferTimeout,
					ssl             = False,
					sslHostname     = None,
				)
			else:
				raise RuntimeError
	def _get(self, id:Any) -> None:
		def wh() -> bool:
			return not self.requests[id].isDone()
		if id not in self.requests:
			raise ResponseError("Unknown request ID: {}".format(id))
		self.socketErrors = 0
		while True:
			try:
				self.signal.check()
				if hasattr(self, "socket") and not self.socket.isAlive():
					del self.socket
				if not hasattr(self, "socket"):
					self._createSocket()
					self._connect()
				self.socket.loop(wh)
				break
			except KillSignal:
				raise
			except BaseRPCError:
				if hasattr(self, "socket"):
					del self.socket
				if self.socketErrors < self.retryCount:
					if self.socketErrors > 0:
						self.log.warn("Error while getting response [{} left]", self.retryCount-self.socketErrors)
						if self.retryDelay:
							self.signal.sleep(self.retryDelay)
					self.socketErrors += 1
					continue
				raise
	def _parseResponse(self, payload:bytes, headers:Optional[T_Headers]=None, charset:str="utf8") -> None:
		if self.requestProtocol in ["JSONRPC-2", "JSONRPC-P"]:
			try:
				data = json.loads(payload.decode(charset))
			except:
				raise ResponseError("Invalid payload")
			if not isinstance(data, list):
				data = [data]
			for r in data:
				if not isinstance(r, dict):
					raise ResponseError("Invalid payload")
				if "id" not in r:
					raise ResponseError("Required data missing: id")
				id = r["id"]
				uid = r.get("uid", None)
				isSuccess = not ("error" in r and r["error"])
				if isSuccess:
					if "result" not in r:
						raise ResponseError("Required data missing: result")
					result = r["result"]
				else:
					result = r["error"]
				self._parseResult(id, isSuccess, result, uid)
		elif self.requestProtocol == "REST":
			try:
				data = json.loads(payload.decode(charset))
			except:
				raise ResponseError("Invalid payload")
			self._parseResult(
				min(( cast(int, x) for x in self.requests.keys() if not self.requests[x].isDone())),
				True,
				data,
				"",
			)
		elif self.requestProtocol == "RAW":
			if self.messageProtocol == "STR":
				try:
					data = payload.decode('utf8')
				except:
					raise ResponseError("Invalid payload")
			else:
				data = payload
			self._parseResult(
				min(( cast(int, x) for x in self.requests.keys() if not self.requests[x].isDone())),
				True,
				data,
				"",
			)
		elif self.requestProtocol == "FSP":
			if self.messageProtocol == "STR":
				payload = bytes.fromhex(payload.decode(charset))
			try:
				_, data = fsPacker.loads(
					payload,
					maxDictSize=0,
					maxOPSize=0,
					maxIndexSize=0,
					recursiveLimit=512,
				)
			except:
				raise ResponseError("Invalid payload")
			if not isinstance(data, list):
				data = [data]
			for chunk in data:
				if isinstance(chunk, tuple) and len(chunk) == 4 and \
				(isinstance(chunk[0], (int, str)) or chunk[0] is None) and \
				isinstance(chunk[1], bool) and \
				(isinstance(chunk[3], str) or chunk[3] is None):
					self._parseResult(*chunk)
				else:
					raise ResponseError("Invalid payload")
		elif self.requestProtocol == "OldFSProtocol":
			if self.messageProtocol == "STR":
				payload = bytes.fromhex(payload.decode(charset))
			resp = pickle.loads(payload)
			if isinstance(resp, tuple) and len(resp) == 3 and \
			isinstance(resp[0], (int, str)) and \
			isinstance(resp[1], bool) and \
			isinstance(resp[2], bytes):
				self._parseResult(resp[0], resp[1], pickle.loads(decompress(resp[2])), "")
			else:
				raise ResponseError("Invalid payload")
	def _parseResult(self, id:Union[int, str], isSuccess:bool, result:Any, uid:str) -> None:
		if id not in self.requests:
			self.log.warn("Got unexpected result id: {}", id)
			return
		obj = self.requests[id]
		self.log.debug("Received result for ID: {} UID: {}".format(id, uid))
		obj._parseResponse( id, isSuccess, result, uid )
	def clear(self) -> None:
		self.requests.clear()
	def clone(self, **kwargs:Any) -> T_Client:
		opts = self.__getstate__()
		opts.update(kwargs)
		return Client(**opts)
	def close(self) -> None:
		if hasattr(self, "socket"):
			self.socket.close()
			del self.socket
		self.clear()
		self.log.debug("Closed")
	__del__ = close
	def request(self, method:str="", args:List[Any]=[], kwargs:Dict[str, Any]={}, id:Optional[Union[str, int]]=None,
	path:str="/", httpMethod:str="POST", httpHeaders:Optional[Dict[str, str]]=None, payload:Any=NoPayload) -> T_Request:
		if self.requestProtocol in ("REST", "RAW"):
			if self.messageProtocol == "HTTP":
				if httpMethod == "POST" and payload is NoPayload:
					raise RequestError("Payload is missing during HTTP POST")
				elif httpMethod != "POST" and payload is not NoPayload:
					raise RequestError("Payload can be only sent only through POST HTTP method")
			elif payload is not NoPayload:
				raise RequestError("Payload is missing")
			id = self.id
			self.id += 1
		else:
			if id is None:
				id = self.id
				self.id += 1
			if type(id) not in [int, str]:
				raise RequestError("Request ID can be only str or int")
			if id in self.requests:
				raise RequestError("Request ID already in use: {}".format(id))
		rHttpHeaders = {}
		for k, v in self.extraHttpHeaders.items():
			rHttpHeaders[k.lower()] = v
		if httpHeaders:
			for k, v in httpHeaders.items():
				rHttpHeaders[k.lower()] = v
		obj = Request(
			self,
			id,
			method,
			args,
			kwargs,
			path,
			httpMethod,
			rHttpHeaders,
			payload,
			self.convertNumbers,
		)
		self.requests[id] = obj
		self.log.info("Request queued: {} [{}]".format(method, id))
		if hasattr(self, "socket"):
			self._sendRequest(obj._dumps(), httpMethod, path, rHttpHeaders)
		return obj
