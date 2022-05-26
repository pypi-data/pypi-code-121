# Built in
import os, sys, re, json, tempfile
from collections import OrderedDict
from typing import Dict, List, Tuple, Any, OrderedDict as T_OrderedDict
# Third party modules
from fsLogger import SimpleLogger, Logger
# Local modules
from . import Client, BaseRPCError, __version__
# Program
PUB_ENV_NAME        = "FECLI_PUBKEY"
SEC_ENV_NAME        = "FECLI_SECKEY"
CACHEPATH_ENV_NAME  = "FECLI_CACHE_PATH"
DISCACHE_ENV_NAME   = "FECLI_CACHE_DISABLE"
CONVERTHEX_ENV_NAME = "FECLI_CONVERT_HEX"
STORAGE_FILE        = os.getenv(CACHEPATH_ENV_NAME, "{}/feclicache.json".format(tempfile.gettempdir()))

__doc__ = """Fusion Explorer command line interface v{version}
Copyright (C) 2021 Fusion Solutions KFT <contact@fusionsolutions.io>
To get license use:
  {selfName} --version

Use optional environment keys {PUB_ENV_NAME} for public key and {SEC_ENV_NAME} for secret. If you use you need set both.
  For set:
    export {PUB_ENV_NAME}="YOUR_PUBLIC_KEY" {SEC_ENV_NAME}="YOUR_SECRET_KEY"
  For unset:
    unset {PUB_ENV_NAME} {SEC_ENV_NAME}

All numbers will be converted into decimal string, but you can use {CONVERTHEX_ENV_NAME} enviroment if you want in hexadecimal:
  export {CONVERTHEX_ENV_NAME}="1"

Available bitmasks:
{bitmasks}

  Example usage:
    BLOCK_EXP,BLOCKLOGS_COUNT,TX_HASH
  or just like a number:
    1280

Method list and bitmask keys are downloaded from the server and are stored in {STORAGE_FILE} file.
For overwrite cache location use:
  export {CACHEPATH_ENV_NAME}="/absolute/path/to/file"
To refresh the cache use:
  {selfName} help
To disable cache run:
  export {DISCACHE_ENV_NAME}=1

Usage:
  {selfName} [--debug] METHOD [PARAMETERS]

You can set every parameter as keyword parameter like `PARAMETER_NAME=VALUE` example:
  {selfName} getBlockByHeight btc height=1 bitmask=BLOCK_EXP,TX_HASH

Methods:"""

class CLIError(Exception): pass

class LevelBitmask:
	data:T_OrderedDict[str, Tuple[int, int, str]] = OrderedDict()
	@classmethod
	def parseByName(cls, data:str) -> int:
		r = 0
		for name in data.split(","):
			r |= toInt(cls.data[name][0])
		return r

class Parameters:
	@staticmethod
	def _bool(data:str) -> bool:
		if data == "1" or data.lower() == "true":
			return True
		elif data == "0" or data.lower() == "false":
			return False
		raise ValueError
	@staticmethod
	def _dict(data:str) -> Any:
		return json.loads(data)
	@staticmethod
	def _bytes(data:str) -> bytes:
		if data[:2].lower() == "0x":
			data = data[2:]
		return bytes.fromhex(data)
	@staticmethod
	def _any(data:str) -> Any:
		return data
	@staticmethod
	def _bitmask(data:str) -> int:
		if data.isdigit():
			return int(data)
		else:
			try:
				return LevelBitmask.parseByName(data)
			except KeyError as err:
				raise CLIError("Bitmask `{}` not found" .format(err))
	@staticmethod
	def _hex(data:str) -> Any:
		data = data.lower()
		if data[:2] != "0x":
			return "0x"+data
		if not re.match("0x[0-9a-f]", data, re.I):
			raise KeyError
		return data
	@classmethod
	def parseType(cls, name:str, typ:str) -> Any:
		if name == "bitmask":
			return cls._bitmask
		return {
			"str":str,
			"bytes":cls._bytes,
			"int":toInt,
			"bool":cls._bool,
			"dict":cls._dict,
			"list":cls._dict,
			"hex":cls._hex,
		}.get(typ, cls._any)
	@classmethod
	def build(cls, methodParams:Tuple[str, str, Any], args:List[Any], kwargs:Dict[str, Any]) -> Dict[str, Any]:
		ret = {}
		for (name, typ, opt), arg in zip(methodParams, args):
			ret[ name ] = cls.parseType(name, typ)(arg)
		for key, val in kwargs.items():
			if key in ret:
				raise CLIError("Duplicate parameter: {}".format(key))
			for name, typ, opt in methodParams:
				if name.lower() == key.lower():
					try:
						ret[ name ] = cls.parseType(name, typ)(val)
					except CLIError as err:
						raise err from None
					except:
						raise CLIError("Parsing input for parameter `{}` has been failed", name)
					break
			else:
				raise CLIError("Unknown parameter: {}".format(key))
		return ret

def printResult(r:Any) -> None:
	if type(r) in [dict, list]:
		print(json.dumps(r, indent=4, sort_keys=True, ensure_ascii=False))
	else:
		print(r)

def toInt(input:Any) -> int:
	if type(input) is int:
		return input
	elif type(input) is str:
		if input[:2].lower() == "0x":
			return int(input, 16)
		return int(input)
	raise RuntimeError

def main() -> None:
	disableCompression = False
	inputs:List[str] = []
	_inputs = sys.argv[:]
	selfName = os.path.basename(_inputs.pop(0))
	#
	s = False
	for inp in _inputs:
		if not s:
			if not inp.startswith("--"):
				s = True
			if inp == "--version":
				return printResult(__version__)
			elif inp == "--debug":
				SimpleLogger()
				disableCompression = True
				continue
		inputs.append(inp)
	if inputs:
		method = inputs.pop(0).lower()
	else:
		method = ""
	args:List[Any] = []
	kwargs:Dict[str, Any] = {}
	for inp in inputs:
		sepPos = inp.find("=")
		if sepPos == -1:
			if kwargs:
				raise CLIError("Arguments must be in front of keyword arguments")
			args.append(inp)
		else:
			kwargs[inp[:sepPos]] = inp[sepPos+1:]
	#
	with Client(
		os.getenv(PUB_ENV_NAME, None),
		os.getenv(SEC_ENV_NAME, None),
		convertNumbers="hex" if os.getenv(CONVERTHEX_ENV_NAME, "0") == "1" else "str",
		disableCompression=disableCompression,
		log=Logger("Client")
	) as c:
		methods = {}
		if os.getenv(DISCACHE_ENV_NAME, "0") != "1" and not (method == "help" and not args and not kwargs):
			try:
				methods, _bitmasks = json.load(open(STORAGE_FILE, 'rt'))
				LevelBitmask.data = OrderedDict(_bitmasks)
			except:
				pass
		if not methods:
			response = c.request("getCLIData")
			if not response.isSuccess():
				raise CLIError("Loading method list failed")
			_methods, _bitmasks = response.get()
			for m in _methods:
				methods[m["name"].lower()] = {
					"name":m["name"],
					"desc":m["desc"],
					"parameters":[ [ param["name"], param["type"], param["optional"] ] for param in m["parameters"] ],
				}
			for n, d in _bitmasks:
				LevelBitmask.data[n] = d
			if not os.getenv(DISCACHE_ENV_NAME, False):
				try:
					json.dump((methods, LevelBitmask.data.items()), open(STORAGE_FILE, 'wt'))
				except:
					pass
		#
		if method in ["", "help"] and not args and not kwargs:
			bitmaskLines:List[Tuple[str, str]] = [
				(
					"{0:>{stack}}{name}".format("", name=bid, stack=toInt(bdet[1])*2),
					bdet[2],
				) for bid, bdet in LevelBitmask.data.items()
			]
			optimalBitmaskIDColumnLength = max([ len(x[0]) for x in bitmaskLines]) if bitmaskLines else 0
			ret = [__doc__.format(
				version=__version__,
				PUB_ENV_NAME=PUB_ENV_NAME,
				SEC_ENV_NAME=SEC_ENV_NAME,
				STORAGE_FILE=STORAGE_FILE,
				DISCACHE_ENV_NAME=DISCACHE_ENV_NAME,
				CACHEPATH_ENV_NAME=CACHEPATH_ENV_NAME,
				CONVERTHEX_ENV_NAME=CONVERTHEX_ENV_NAME,
				selfName=selfName,
				bitmasks="\n".join(["  {0:<{pad}}    {1}".format(*x, pad=optimalBitmaskIDColumnLength) for x in bitmaskLines]),
			)]
			for name in sorted(methods.keys()):
				m = methods[name]
				ret.append(
					"  {} {}\n      {}\n".format(
						m["name"],
						" ".join([
							("{o1}({type}){name}{o2}").format(
								type=typ.upper(),
								name=name,
								o1="[" if opt else "",
								o2="]" if opt else ""
							) for name,typ,opt in m["parameters"]
						]),
						m["desc"]
					)
				)
			return printResult("\n".join(ret))
		if method not in methods:
			raise CLIError("Method not found. For list of methods use `{} help`".format(selfName))
		response = c.request(
			methods[method]["name"],
			[],
			Parameters.build(
				methods[method]["parameters"],
				args,
				kwargs
			),
		)
		if not response.isSuccess():
			print("Request failed:")
		c.close()
		c.log.debug("RESPONSE UID: {}".format(response.getUID()))
		return printResult(response.get())

r = None
c = 0
try:
	main()
except CLIError as err:
	print("CLI ERROR: {}".format(err))
except BaseRPCError as err:
	c = 1
	printResult(err)
except KeyboardInterrupt:
	c = 1
	print("Keyboard interrupt")
sys.exit(c)
