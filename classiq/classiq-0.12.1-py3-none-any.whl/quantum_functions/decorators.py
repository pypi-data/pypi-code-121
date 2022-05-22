from typing import Callable, Optional, Union, overload

from classiq.quantum_functions.quantum_function import QuantumFunction


@overload
def quantum_function(func: None = None, name: Optional[str] = None) -> Callable:
    ...


@overload
def quantum_function(func: Callable, name: Optional[str] = None) -> QuantumFunction:
    ...


def quantum_function(
    func: Optional[Callable] = None, name: Optional[str] = None
) -> Union[QuantumFunction, Callable]:
    if func is None:
        return lambda func: quantum_function(func, name)
    else:
        qf = QuantumFunction()
        qf.add_implementation(func, name)
        return qf
