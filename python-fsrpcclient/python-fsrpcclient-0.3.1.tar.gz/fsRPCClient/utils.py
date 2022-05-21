# Builtin modules
from __future__ import annotations
import zlib
from typing import Dict, Any, List, Tuple, Iterator, Iterable, Optional, Generator, cast
# Local modules
from .abcs import T_Headers
# Program
class Headers(T_Headers):
	def __init__(self, initial:Dict[str, str]={}):
		self.data = {}
		for k, v in initial.items():
			self[k.lower()] = v
	def __setitem__(self, k:str, v:str) -> None:
		self.data[k.lower()] = v
		return None
	def __getitem__(self, k:str) -> str:
		return self.data[k.lower()]
	def __delitem__(self, k:str) -> None:
		del self.data[k.lower()]
	def __iter__(self) -> Iterator[str]:
		return self.data.__iter__()
	def has_key(self, k:str) -> bool:
		return k.lower() in self.data
	__contains__ = has_key
	def keys(self) -> Iterable[str]:
		return self.data.keys()
	def values(self) -> Iterable[str]:
		return self.data.values()
	def items(self) -> Iterable[Tuple[str, str]]:
		return self.data.items()
	def get(self, k:str, default:Optional[str]=None) -> str:
		k = k.lower()
		if k not in self.data:
			return cast(str, default)
		return self.data[k]
	def update(self, m:Dict[str, str]) -> Headers:
		for k, v in m.items():
			self.data[k.lower()] = v
		return self
	def dumps(self, extend:Dict[str, str]={}) -> str:
		h:List[str] = []
		for k, v in self.data.items():
			h.append("{}: {}".format(k, v))
		for k, v in extend.items():
			h.append("{}: {}".format(k.lower(), v))
		return "\r\n".join(h)

class deflate:
	@staticmethod
	def compress(data:bytes) -> bytes:
		o = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
		r = o.compress(data)
		r += o.flush()
		return r
	@staticmethod
	def decompress(data:bytes) -> bytes:
		o = zlib.decompressobj(-zlib.MAX_WBITS)
		r = o.decompress(data)
		r += o.flush()
		return r

def hexToBytes(data:str) -> bytes:
	if data[:2].lower() == "0x":
		data = data[2:]
	return bytes.fromhex(data)

def iterSplit(l:List[Any], n:int) -> Generator[Any, List[Any], None]:
	for i in range(0, len(l), n):
		yield(l[i:i+n])
