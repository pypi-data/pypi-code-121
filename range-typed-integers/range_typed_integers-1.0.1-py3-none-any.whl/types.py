from dataclasses import dataclass
from typing import NewType, Protocol, TypeVar, Generic

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


class Comparable(Protocol):
    def __eq__(self, o: object) -> bool: ...
    def __lt__(self, o: object) -> bool: ...
    def __le__(self, o: object) -> bool: ...
    def __gt__(self, o: object) -> bool: ...
    def __ge__(self, o: object) -> bool: ...


T = TypeVar('T', bound=Comparable)


@dataclass
class ValueRange(Generic[T]):
    """Type annotation. The type is only valid for values between self.min and self.max (inclusive)."""
    min: T
    max: T


u8 = NewType('u8', Annotated[int, ValueRange(0, 255)])
i8 = NewType('i8', Annotated[int, ValueRange(-128, 127)])
u16 = NewType('u16', Annotated[int, ValueRange(0, 65_535)])
i16 = NewType('i16', Annotated[int, ValueRange(-32_768, 32_767)])
u32 = NewType('u32', Annotated[int, ValueRange(0, 4_294_967_295)])
i32 = NewType('i32', Annotated[int, ValueRange(-2_147_483_648, 2_147_483_647)])
u64 = NewType('u64', Annotated[int, ValueRange(0, 18_446_744_073_709_551_615)])
i64 = NewType('i64', Annotated[int, ValueRange(-9_223_372_036_854_775_808, 9_223_372_036_854_775_807)])
