import enum
from typing import Callable, Dict, List, Optional, Union

import pydantic


class MetricsRegisterRole(str, enum.Enum):
    INPUT = "input"
    OUTPUT = "output"
    AUXILIARY = "auxiliary"
    ZERO = "zero"


class MetricsRegister(pydantic.BaseModel):
    role: MetricsRegisterRole
    name: str
    qubit_indexes_relative: List[int]
    qubit_indexes_absolute: List[int] = list()

    def __len__(self):
        return self.qubit_indexes_relative.__len__()

    @property
    def width(self):
        return len(self)


class FunctionMetrics(pydantic.BaseModel):
    name: str
    registers: List[MetricsRegister] = list()
    depth: Optional[int]
    width: Optional[int]
    released_auxiliary_qubits: List[int] = list()

    def __getitem__(self, key):
        if type(key) is int:
            return self.registers[key]
        if type(key) is str:
            for register in self.registers:
                if key == register.name:
                    return register
        raise KeyError(key)

    def _update_registers(self, absolute_index_getter: Callable[[int], int]):
        for r in self.registers:
            r.qubit_indexes_absolute = list(
                map(absolute_index_getter, r.qubit_indexes_relative)
            )


class SynthesisMetrics(pydantic.BaseModel):
    duration_in_seconds: Optional[float]
    failure_reason: Optional[str]
    topological_sort: Optional[List[str]]
    function_metrics: List[FunctionMetrics] = pydantic.Field(default_factory=list)
    _function_mapping: Dict[
        Optional[Union[int, str]], FunctionMetrics
    ] = pydantic.PrivateAttr(default_factory=dict)

    def __getitem__(self, key) -> FunctionMetrics:
        if not self._function_mapping:
            for i, fm in enumerate(self.function_metrics):
                self._function_mapping[i] = fm
                self._function_mapping[fm.name] = fm

        try:
            return self._function_mapping[key]
        except KeyError:
            close_to_key = [
                map_key
                for map_key in self._function_mapping
                if isinstance(map_key, str) and map_key.startswith(key)
            ]
            if len(close_to_key) == 0:
                raise KeyError(f"No function named {key}")
            elif len(close_to_key) == 1:
                return self._function_mapping[close_to_key[0]]
            else:
                raise KeyError(f"Multiple function named {key} found, {close_to_key}")

    def __len__(self):
        return self.function_metrics.__len__()

    def __iter__(self):
        if not self.topological_sort:
            return
        yield from (self[function_name] for function_name in self.topological_sort)

    def _update_registers(self, qubit_absolute_indexes: Dict[str, List[int]]):
        for fm in self.function_metrics:
            absolute_index_getter = qubit_absolute_indexes[fm.name].__getitem__
            fm._update_registers(absolute_index_getter)

    def pprint(self):
        print("Circuit Synthesis Metrics")
        print(f"    Generation took {self.duration_in_seconds} seconds")
        if self.failure_reason:
            print("Generation failed :(")
            print(f"Failure reason: {self.failure_reason}")
            return
        print(f"The circuit has {len(self.function_metrics)} functions:")
        for index, fm in enumerate(self.function_metrics):
            print(f"{index}) {fm.name}")
            if fm.name != "OUT":
                print(
                    f"  depth: {fm.depth} ; width: {fm.width} ; registers: {len(fm.registers)}"
                )
                for reg_index, register in enumerate(fm.registers):
                    print(
                        f"  {reg_index}) {register.role.value} - {register.name} ; qubits: {register.qubit_indexes_absolute}"
                    )
