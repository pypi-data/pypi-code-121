import io
import sys
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any


@dataclass
class FunctionComponents:
    std_out: io.StringIO
    exception: Optional[Any] = None


def capture_function(function: Callable, params: Optional[Dict] = None) -> FunctionComponents:
    """
    Helper function to capture standard out and any exceptions from a function
    """
    exception = None
    std_out = io.StringIO()

    sys.stdout = std_out
    try:
        function(**(params or {}))
    except Exception as err:
        exception = err
    sys.stdout = sys.__stdout__
    return FunctionComponents(std_out=std_out, exception=exception)
