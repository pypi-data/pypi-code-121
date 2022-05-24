from typing import Tuple, Any, Dict, Callable, TypeVar

# The type of a standard *args parameter
POSITIONAL_ARGS_TYPE = Tuple[Any, ...]

# The type of a standard **kwargs parameter
KEYWORD_ARGS_TYPE = Dict[str, Any]

# The type of *args, **kwargs combined
VAR_ARGS_TYPE = Tuple[POSITIONAL_ARGS_TYPE, KEYWORD_ARGS_TYPE]

# The type of a callable (non-generic)
AnyCallable = Callable[[Any], Any]

# The generic type of arguments to a callable
ArgType = TypeVar("ArgType")

# The generic return type of a callable
ReturnType = TypeVar("ReturnType")

# The type of a generic callable
GenericCallable = Callable[[ArgType], ReturnType]

# The type of a generic decorator function
GenericDecorator = Callable[[GenericCallable], GenericCallable]
