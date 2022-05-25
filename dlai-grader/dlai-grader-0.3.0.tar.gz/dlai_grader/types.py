from types import ModuleType
from typing import Any, Callable, List, Optional
from .grading import test_case

grading_function = Callable[[Any], List[test_case]]
grading_wrapper = Callable[[ModuleType, Optional[ModuleType]], grading_function]
