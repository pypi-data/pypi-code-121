# Builtin modules
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from selectors import BaseSelector
from ssl import SSLSession
from weakref import WeakValueDictionary
from typing import List, Dict, Tuple, Union, Callable, Optional, Any, NoReturn, Iterable, Iterator
# Third party modules
from fsLogger import T_Logger
from fsSignal import T_Signal
# Local modules
# Program
T_SocketBindAddress_TCPv4 = Tuple[str, int]
T_SocketBindAddress_TCPv6 = Tuple[str, int, int, int]
T_SocketBindAddress = Union[T_SocketBindAddress_TCPv4, T_SocketBindAddress_TCPv6]

class T_Socket(metaclass=ABCMeta):
	def __init__(self, family:int=..., type:int=..., proto:int=..., fileno:Optional[int]=...) -> None: ...
	@abstractmethod
	def fileno(self) -> int: ...
	@abstractmethod
	def do_handshake(self) -> None: ...
	@abstractmethod
	def close(self) -> None: ...
	@abstractmethod
	def setblocking(self, __flag:bool) -> None: ...
	@abstractmethod
	def setsockopt(self, __level:int, __optname:int, __value:Union[int, bytes]) -> None: ...
	@abstractmethod
	def send(self, __data:bytes, __flags:int=...) -> int: ...
	@abstractmethod
	def recv(self, __bufsize:int, __flags:int=...) -> bytes: ...
	@abstractmethod
	def connect_ex(self, __address:Union[Tuple[Any, ...], str]) -> int: ...
	@abstractmethod
	def shutdown(self, __how:int) -> None: ...
	@abstractmethod
	def bind(self, __address:T_SocketBindAddress) -> None: ...
	@abstractmethod
	def getsockname(self) -> T_SocketBindAddress: ...

class SSLContext(metaclass=ABCMeta):
	def wrap_socket(self, sock:T_Socket, server_side:bool=..., do_handshake_on_connect:bool=..., suppress_ragged_eofs:bool=...,
	server_hostname:Optional[str]=..., session:Optional[SSLSession]=...) -> T_Socket: ...

class NoPayload: ...

class T_Client(metaclass=ABCMeta):
	max_bulk_request:int
	FSPACKER_VERSION:int
	target:Union[str, Tuple[str, int], Tuple[str, int, int, int]]
	protocol:str
	connTimeout:float
	transferTimeout:float
	retryDelay:float
	retryCount:int
	socketErrors:int
	ssl:bool
	sslHostname:Optional[str]
	httpHost:Optional[str]
	extraHttpHeaders:Dict[str, str]
	disableCompression:bool
	useBulkRequest:bool
	convertNumbers:Optional[str]
	log:T_Logger
	signal:T_Signal
	id:int
	requests:WeakValueDictionary[Optional[Union[str, int]], T_Request]
	socket:Union[T_BaseClientSocket_send_default, T_BaseClientSocket_send_http]
	socketProtocol:str
	messageProtocol:str
	requestProtocol:str
	@abstractmethod
	def _initializeProtocol(self) -> None: ...
	@abstractmethod
	def __enter__(self) -> T_Client: ...
	@abstractmethod
	def __exit__(self, type:Any, value:Any, traceback:Any) -> None: ...
	@abstractmethod
	def __del__(self) -> None: ...
	@abstractmethod
	def __getstate__(self) -> Dict[str, Any]: ...
	@abstractmethod
	def __setstate__(self, states:Dict[str, Any]) -> None: ...
	@abstractmethod
	def _connect(self, sendOlderRequests:bool=...) -> None: ...
	@abstractmethod
	def _sendRequest(self, data:Any, httpMethod:str=..., path:str=..., httpHeaders:Dict[str, str]=...) -> None: ...
	@abstractmethod
	def _sendToSocket(self, payload:bytes, httpMethod:str=..., path:str=..., httpHeaders:Dict[str, str]=...) -> None: ...
	@abstractmethod
	def _createSocket(self) -> None: ...
	@abstractmethod
	def _get(self, id:Any) -> None: ...
	@abstractmethod
	def _parseResponse(self, payload:bytes, headers:Optional[T_Headers]=..., charset:str=...) -> None: ...
	@abstractmethod
	def _parseResult(self, id:Union[int, str], isSuccess:bool, result:Any, uid:str) -> None: ...
	@abstractmethod
	def clear(self) -> None: ...
	@abstractmethod
	def clone(self, **kwargs:Any) -> T_Client: ...
	@abstractmethod
	def close(self) -> None: ...
	def request(self, method:str=..., args:List[Any]=..., kwargs:Dict[str, Any]=..., id:Optional[Union[str, int]]=...,
	path:str=..., httpMethod:str=..., httpHeaders:Optional[Dict[str, str]]=..., payload:Any=...) -> T_Request: ...

class T_BaseClientSocket(metaclass=ABCMeta):
	client:T_Client
	protocol:str
	target:Union[str, Tuple[str, int], Tuple[str, int, int, int]]
	connTimeout:float
	transferTimeout:float
	ssl:bool
	sslHostname:Optional[str]
	bind:Optional[T_SocketBindAddress]
	log:T_Logger
	signal:T_Signal
	poll:BaseSelector
	readBuffer:bytes
	writeBuffer:bytes
	connectionStatus:int
	timeoutTimer:float
	sock:T_Socket
	sockFD:Optional[int]
	mask:int
	sslTimer:float
	@abstractmethod
	def _connect(self, initial:bool=False) -> bool: ...
	@abstractmethod
	def _createSocket(self) -> None: ...
	@abstractmethod
	def _doSSLHandshake(self) -> bool: ...
	@abstractmethod
	def _haveRead(self) -> bool: ...
	@abstractmethod
	def _haveWrite(self) -> bool: ...
	@abstractmethod
	def _raiseSocketError(self, err:str) -> NoReturn: ...
	@abstractmethod
	def _raiseMessageError(self, err:str) -> NoReturn: ...
	@abstractmethod
	def _reset(self) -> None: ...
	@abstractmethod
	def _setMask(self, newMask:int) -> None: ...
	@abstractmethod
	def _write(self, data:bytes) -> None: ...
	@abstractmethod
	def close(self) -> None: ...
	@abstractmethod
	def connect(self) -> None: ...
	@abstractmethod
	def _isConnected(self) -> bool: ...
	@abstractmethod
	def isAlive(self) -> bool: ...
	@abstractmethod
	def loop(self, whileFn:Callable[[], bool]) -> None: ...
	@abstractmethod
	def parseReadBuffer(self) -> bool: ...

class T_BaseClientSocket_send_default(T_BaseClientSocket, metaclass=ABCMeta):
	@abstractmethod
	def send(self, payload:bytes) -> None: ...

class T_BaseClientSocket_send_http(T_BaseClientSocket, metaclass=ABCMeta):
	@abstractmethod
	def send(self, payload:bytes=b"", httpMethod:str=..., path:str=..., headers:Dict[str, str]=...) -> None: ...

class T_HTTPClientSocket(T_BaseClientSocket_send_http, metaclass=ABCMeta):
	defaultHeaders:Dict[str, str]
	headers:T_Headers
	@abstractmethod
	def send(self, payload:bytes=b"", httpMethod:str=..., path:str=..., headers:Dict[str, str]=...) -> None: ...

class T_StringClientSocket(T_BaseClientSocket_send_default, metaclass=ABCMeta):
	pass

class T_FSPackerClientSocket(T_BaseClientSocket_send_default, metaclass=ABCMeta):
	pass

class T_OldFSPackerClientSocket(T_BaseClientSocket_send_default, metaclass=ABCMeta):
	@abstractmethod
	def _readResponse(self) -> Tuple[int, bytes]: ...
	@abstractmethod
	def _encodeRequest(self, buffer:bytes) -> bytes: ...

class T_Headers(metaclass=ABCMeta):
	data:Dict[str, str]
	@abstractmethod
	def __setitem__(self, k:str, v:str) -> None: ...
	@abstractmethod
	def __getitem__(self, k:str) -> str: ...
	@abstractmethod
	def __contains__(self, k:str) -> bool: ...
	@abstractmethod
	def __delitem__(self, k:str) -> None: ...
	@abstractmethod
	def __iter__(self) -> Iterator[str]: ...
	@abstractmethod
	def has_key(self, k:str) -> bool: ...
	@abstractmethod
	def keys(self) -> Iterable[str]: ...
	@abstractmethod
	def values(self) -> Iterable[str]: ...
	@abstractmethod
	def items(self) -> Iterable[Tuple[str, str]]: ...
	@abstractmethod
	def get(self, k:str, default:Optional[str]=None) -> str: ...
	@abstractmethod
	def update(self, m:Dict[str, str]) -> T_Headers: ...
	@abstractmethod
	def dumps(self, extend:Dict[str, str]={}) -> str: ...

class T_Request(metaclass=ABCMeta):
	_client:T_Client
	_id:Optional[Union[str, int]]
	_method:str
	_args:List[Any]
	_kwargs:Dict[Any, Any]
	_path:str
	_httpMethod:str
	_httpHeaders:Dict[str, str]
	_payload:str
	_convertNumbers:Optional[str]
	_requestTime:float
	_responseTime:float
	_uid:str
	_done:bool
	_success:bool
	_response:Any
	@abstractmethod
	def _get(self) -> None: ...
	@abstractmethod
	def _parseResponse(self, id:Union[int, str], isSuccess:bool, result:Any, uid:str) -> None: ...
	@abstractmethod
	def _dumps(self) -> Any: ...
	@abstractmethod
	def get(self) -> Any: ...
	@abstractmethod
	def getDelay(self) -> float: ...
	@abstractmethod
	def getID(self) -> Any: ...
	@abstractmethod
	def isDone(self) -> bool: ...
	@abstractmethod
	def getUID(self) -> str: ...
	@abstractmethod
	def isSuccess(self) -> bool: ...
