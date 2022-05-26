from typing import overload
from typing import List
from .WorldScanner import WorldScanner


class WorldScannerBuilder:
	"""The builder can be used to create a world scanner with native java functions. This is especially useful for languages like javascript that
don't support multithreading, which causes streams to run sequential instead of parallel.
The builder has two filters for the block and the block state, which need to be configured separately.
If one function is not defined, it will just be ignored when building the scanner. The block and block state filters have to start with a 'with' command like WorldScannerBuilder#withStateFilter(java.lang.String) or WorldScannerBuilder#withStringBlockFilter() .
This will overwrite all previous filters of the same type. To add more commands, it's possible to use commands with the prefix 'and', 'or', 'xor'.
The 'not' command will just negate the whole block or block state filter and doesn't need any arguments.  
All other commands need some arguments to work. For String functions, it's one of these functions: 'equals', 'contains', 'startsWith', 'endsWith' or 'matches'.
The strings to match are passed as vararg parameters (as many as needed, separated by a comma 'is("chest", "barrel", "ore"' ) and the filter acts
like a logical or, so only one of the arguments needs to match the criteria. It should be noted, that string functions call the toString method, so
comparing a block with something like "minecraft:stone" will always return false, because the toString method gives "{minecraft:stone}". For doing this
use either contains or the equals method with 'getId', as shown later. This will match any block that includes 'stone' or 'diorit' in its name: withStringBlockFilter().contains("stone") //create new block filter, check if it contains stone
.orStringBlockFilter().contains("diorit") //append new block filter with or and check if it contains diorit  
For non String functions, the method name must be passed when creating the filter. The names can be any method in BlockStateHelper or BlockHelper .
For more complex filters, use the MethodWrapper function FWorld#getWorldScanner(xyz.wagyourtail.jsmacros.core.MethodWrapper<xyz.wagyourtail.jsmacros.client.api.helpers.BlockHelper,java.lang.Object,java.lang.Boolean,?>,xyz.wagyourtail.jsmacros.core.MethodWrapper<xyz.wagyourtail.jsmacros.client.api.helpers.BlockStateHelper,java.lang.Object,java.lang.Boolean,?>) .
Depending on the return type of the method, the following parameters must be passed to 'is' or 'test'. There are two methods, because 'is' is a keyword in some languages.  For any number:
  - is(operation, number) with operation = '>', '>=', ' ', ' =', '==', '!=' and the number that should be compared to,
    i.e. is(">=", 8) returns true if the returned number is greater or equal to 8.
For any String:
  - is(method, string) with method = 'EQUALS', 'CONTAINS', 'STARTS_WITH', 'ENDS_WITH', 'MATCHES' and the string is the one to compare the returned value to,
    i.e. is("ENDS_WITH", "ore") checks if the returned string ends with ore (can be used with withBlockFilter("getId")).
For any Boolean:
  - is(val) with val either 'true' or 'false' is(false) returns true if the returned boolean value is false\n
	Since: 1.6.5 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def withStateFilter(self, method: str) -> "WorldScannerBuilder":
		pass

	@overload
	def andStateFilter(self, method: str) -> "WorldScannerBuilder":
		pass

	@overload
	def orStateFilter(self, method: str) -> "WorldScannerBuilder":
		pass

	@overload
	def notStateFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def withBlockFilter(self, method: str) -> "WorldScannerBuilder":
		pass

	@overload
	def andBlockFilter(self, method: str) -> "WorldScannerBuilder":
		pass

	@overload
	def orBlockFilter(self, method: str) -> "WorldScannerBuilder":
		pass

	@overload
	def notBlockFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def withStringBlockFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def andStringBlockFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def orStringBlockFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def withStringStateFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def andStringStateFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def orStringStateFilter(self) -> "WorldScannerBuilder":
		pass

	@overload
	def is_(self, args: List[object]) -> "WorldScannerBuilder":
		pass

	@overload
	def is_(self, methodArgs: List[object], filterArgs: List[object]) -> "WorldScannerBuilder":
		pass

	@overload
	def test(self, args: List[object]) -> "WorldScannerBuilder":
		pass

	@overload
	def test(self, methodArgs: List[object], filterArgs: List[object]) -> "WorldScannerBuilder":
		pass

	@overload
	def equals(self, args: List[str]) -> "WorldScannerBuilder":
		pass

	@overload
	def contains(self, args: List[str]) -> "WorldScannerBuilder":
		pass

	@overload
	def startsWith(self, args: List[str]) -> "WorldScannerBuilder":
		pass

	@overload
	def endsWith(self, args: List[str]) -> "WorldScannerBuilder":
		pass

	@overload
	def matches(self, args: List[str]) -> "WorldScannerBuilder":
		pass

	@overload
	def build(self) -> WorldScanner:
		pass

	pass


