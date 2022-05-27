import abc
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Mapping,
    NamedTuple,
    Optional,
    ParamSpec,
    Sequence,
    Type,
    TypeVar,
    Union,
)

_MapperParams = ParamSpec("_MapperParams")
_In = TypeVar("_In")
_Out = TypeVar("_Out")
_New = TypeVar("_New")
_Left = TypeVar("_Left")
_Right = TypeVar("_Right")


class Mapper(Generic[_In, _Out], abc.ABC):
    """A mapper abstract class.

    Example:
    >>> class MultiplyMapper(Mapper):
    ...     def map_item(self, num, **kwargs):
    ...         return num*2
    ...
    >>> mapper=MultiplyMapper()
    >>> mapper(2)
    4
    >>> mapper(5)
    10
    >>> mapper.reverse_map(4)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    NotImplementedError: ...
    """

    def __call__(self, input: _In, **kwds: Any) -> _Out:
        """Process the input argument.

        Args:
            input: The object being processed.

        Returns:
            _Out: The resulting object.
        """
        return self.map_item(input, **kwds)

    @abc.abstractmethod
    def map_item(self, item: _In, **kwargs: Any) -> _Out:
        """Maps an item to it's output representation.

        Args:
            item (_In): The item to map.

        Returns:
            _Out: The output representation.
        """

    def reverse_map(self, out: _Out, **kwargs: Any) -> _In:
        """Reverse the mapping process.

        Args:
            out (_Out): The output to reverse map.

        Returns:
            _In: The input representation.
        """
        raise NotImplementedError("Not implemented.")

    def chain(
        self,
        mapper: Union[
            Callable[[_Out], _New],
            Type["Mapper[_Out, _New]"],
        ],
        *mapper_args: Any,
        **mapper_kwargs: Any
    ) -> "Mapper[_In,_New]":
        """Chain another mapper to this.

        >>> mapper=(
        ...     LambdaMapper(lambda x: x*2, lambda x: x/2)
        ...     .chain(LambdaMapper, lambda x: x*2, lambda x: x/2)
        ... )
        >>> mapper(3)
        12
        >>> mapper.reverse_map(12)
        3.0

        You can also chain a mapper instance:
        >>> mapper2=mapper.chain(LambdaMapper(lambda x: x*2, lambda x: x/2))
        >>> mapper2(3)
        24
        >>> mapper2.reverse_map(24)
        3.0

        A plain callable gets wrapped in a lambda mapper:
        >>> mapper3 = mapper2.chain(lambda x: x*2, reverse_func=lambda: x/2)
        >>> mapper3(3)
        48

        Raises if any other type is provided.
        >>> mapper.chain('x')
        Traceback (most recent call last):
          ...
        TypeError: ...
        >>>
        """
        if callable(mapper):
            if isinstance(mapper, Mapper):
                mapper_instance = mapper
            else:
                if isinstance(mapper, type):
                    mapper_instance = mapper(
                        *mapper_args,
                        **mapper_kwargs,
                    )  # type: ignore
                else:
                    # Assume that this is a plain mapper function.
                    reverse_func = mapper_kwargs.pop("reverse_func", None)
                    mapper_instance = LambdaMapper(
                        mapper,
                        reverse_func,
                        *mapper_args,
                        **mapper_kwargs,
                    )
        else:
            raise TypeError(
                "Invalid value for the `mapper` parameter. Must be a mapper factory or"
                "class."
            )

        return DecoratedMapper(self, mapper_instance)

    def __invert__(self) -> "Mapper[_Out, _In]":
        """Return the inverse mapper.

        Returns:
            Mapper[_Out, _In]: A mapper doing the reverse operation.

        For example, this inverts the lambda operation.
        >>> mapper = ~LambdaMapper(lambda x: x*2, lambda x: x/2)
        >>> mapper(4)
        2.0
        >>> reversed_mapper = ~mapper # (Reverse the mapper)
        >>> reversed_mapper(4)
        8
        >>>
        """
        return InverseMapper(self)

    def __rshift__(
        self, other: "Mapper[_Left, _In]"
    ) -> "Mapper[_Left, _Out]":  # pragma nocover
        """Chain this mapper to the right of the other.

        Args:
            other (Mapper[_New, _In]): The mapper to chain to the left.

        Returns:
            Mapper[_New, _Out]: The mapper chain.
        """
        return other.chain(self)  # type: ignore

    def __lshift__(
        self, other: "Mapper[_Out, _Right]"
    ) -> "Mapper[_In, _Right]":  # pragma nocover
        """Chain this mapper to the left of the other.

        Args:
            other: The mapper to prepend.

        Returns:
            Mapper[_New, _Out]: The mapper chain.
        """
        return self.chain(other)  # type: ignore

    @staticmethod
    def identity():  # pragma nocover
        return LambdaMapper(lambda x: x, lambda x: x)


@dataclass(frozen=True)
class LambdaMapper(Mapper[_In, _Out]):
    """A lambda-powered mapper.

    A multiply mapper can be defined as follows:
    >>> mapper=LambdaMapper(lambda x: x*3, lambda x: x/3)

    Example call:
    >>> mapper(4)
    12
    >>> mapper.reverse_map(15)
    5.0

    If the `reverse_func` param is not provided, a `NotImplementedError` is raised.
    >>> mapper2 = LambdaMapper(lambda x: x*3)
    >>> mapper2.reverse_map(3)
    Traceback (most recent call last):
      ...
    NotImplementedError: ...

    A multiply x*n mapper can be defined as follows:
    >>> mapper3 = LambdaMapper(
    ...     lambda x, *, n: x*n,
    ...     lambda x, *, n: x/n,
    ... )
    >>> mapper3(4, n=5)
    20
    >>> mapper3.reverse_map(20, n=5)
    4.0
    >>> mapper3(4)
    Traceback (most recent call last):
      ...
    TypeError: ...

    With a pre-populated `n` argument:
    >>> mapper4 = LambdaMapper(
    ...     mapper3.func, mapper3.reverse_func,
    ...     mapper_kwargs={'n': 5}
    ... )
    >>> mapper4(4)
    20
    """

    func: Callable[[_In], _Out]
    reverse_func: Optional[Callable[[_Out], _In]] = None
    mapper_kwargs: Mapping[str, Any] = field(default_factory=dict)

    def map_item(self, item: _In, **kwargs: Any) -> _Out:
        return self.func(item, **self._merge_kwargs(kwargs))

    def _merge_kwargs(self, kwargs: Mapping[str, Any]) -> Mapping[str, Any]:
        extra_kwargs = {**self.mapper_kwargs}

        extra_kwargs.update(kwargs)

        return extra_kwargs

    def reverse_map(self, out: _Out, **kwargs: Any) -> _In:
        if self.reverse_func is not None:
            return self.reverse_func(out, **self._merge_kwargs(kwargs))
        return super().reverse_map(out)


_Obj = TypeVar("_Obj")


class _Arguments(NamedTuple):
    args: tuple
    kwargs: Dict[str, Any]


class ToFunctionArgsMapper(Mapper[dict[str, Any] | Sequence, _Arguments]):
    """Maps a dict to kwargs part of a function call.

    Example:
    >>> mapper=ToFunctionArgsMapper()

    >>> mapper({'x':3})
    _Arguments(args=(), kwargs={'x': 3})
    >>> mapper([3])
    _Arguments(args=(3,), kwargs={})
    >>> mapper({3})
    _Arguments(args=(3,), kwargs={})
    >>> mapper((3,))
    _Arguments(args=(3,), kwargs={})
    >>> args, kwargs = mapper((3,), x=2)

    >>> kwargs['x']
    2
    >>> mapper('x')
    Traceback (most recent call last):
      ...
    TypeError: ...
    >>>
    """

    def map_item(self, item, **default_kwargs):
        args: list[Any] = []
        kwargs: dict[str, Any] = {}
        kwargs.update(default_kwargs)
        if isinstance(item, dict):
            kwargs.update(item)
        elif isinstance(item, (tuple, list, set)):
            args.extend(item)
        else:
            raise TypeError("Type not supported.")

        return _Arguments(tuple(args), kwargs)


class ConstructorMapper(Mapper[_Arguments, _Obj], Generic[_Obj]):
    """A from-args to object mapper.

    Example:
    >>> from dataclasses import dataclass

    >>> @dataclass()
    ... class Point:
    ...     x: int
    ...     y: int
    ...
    >>> mapper=ConstructorMapper(Point)

    >>> mapper(((4, 5),{}))
    Point(x=4, y=5)
    >>> mapper(((4,),{'y': 5}))
    Point(x=4, y=5)
    >>> mapper(((),{'y': 5,'x':4}))
    Point(x=4, y=5)

    Non-clas objects are not accepted:
    >>> mapper2 = ConstructorMapper(lambda x, y: (x, y))
    Traceback (most recent call last):
      ...
    AssertionError: ...
    """

    def __init__(self, cls: Type[_Obj]) -> None:
        super().__init__()
        if not isinstance(cls, type):
            raise AssertionError("The provided object is not a valid class.")
        self.cls = cls

    def map_item(self, item: _Arguments, **kwargs: Any) -> _Obj:
        args, kw = item
        return self.cls(*args, **kw)  # type: ignore


_Intermediate = TypeVar("_Intermediate")


class DecoratedMapper(Mapper[_In, _Out]):
    """Wraps two other mappers, effectively producing a binaary tree of mappers.

    Example:
    >>> left = LambdaMapper(lambda x: x*2, lambda x: x/2)
    >>> right = LambdaMapper(lambda x: x*3, lambda x: x/3)
    >>> decorated = DecoratedMapper(left, right)
    >>> decorated(2)
    12
    >>> decorated.reverse_map(12)
    2.0

    But non-mapper instances are not accepted:
    >>> class FakeMapper:
    ...     pass
    ...
    >>> decorated2=DecoratedMapper(left, FakeMapper())
    Traceback (most recent call last):
      ...
    TypeError: ...
    >>> decorated2=DecoratedMapper(FakeMapper(), right)
    Traceback (most recent call last):
      ...
    TypeError: ...
    >>>
    """

    def __init__(
        self, first: Mapper[_In, _Intermediate], second: Mapper[_Intermediate, _Out]
    ) -> None:
        super().__init__()
        if not isinstance(first, Mapper):
            raise TypeError("The left mapper is not a valid mapper instance.")
        if not isinstance(second, Mapper):
            raise TypeError("The right-side mapper is not a valid mapper instance.")

        self.first, self.second = first, second

    def map_item(self, item: _In, **kwargs: Any) -> _Out:
        return self.second.map_item(self.first.map_item(item, **kwargs), **kwargs)

    def reverse_map(self, out: _Out, **kwargs: Any) -> _In:
        return self.first.reverse_map(self.second.reverse_map(out, **kwargs), **kwargs)


class InverseMapper(Mapper[_Out, _In], Generic[_In, _Out]):
    """A reverse mapper.

    This performs the inverse operation from the given mapper by calling the
    `reverse_map` method.

    Normally, this is not instantiated directly. Insthead, use the `inverse` operator.
    """

    def __init__(self, mapper: Mapper[_In, _Out]) -> None:
        super().__init__()
        self.mapper = mapper

    def map_item(self, item: _Out, **kwargs: Any) -> _In:
        return self.mapper.reverse_map(item, **kwargs)

    def reverse_map(self, out: _In, **kwargs: Any) -> _Out:
        return self.mapper.map_item(out, **kwargs)
