from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .Option import Option

Field = TypeVar["java.lang.reflect.Field"]
T = TypeVar("T")
Method = TypeVar["java.lang.reflect.Method"]

class SettingsOverlay_SettingField(Generic[T]):
	type: Class
	option: Option

	@overload
	def __init__(self, option: Option, containingClass: object, f: Field, getter: Method, setter: Method, type: Class) -> None:
		pass

	@overload
	def set(self, o: T) -> None:
		pass

	@overload
	def get(self) -> T:
		pass

	@overload
	def hasOptions(self) -> bool:
		pass

	@overload
	def getOptions(self) -> List[T]:
		pass

	@overload
	def isSimple(self) -> bool:
		pass

	pass


