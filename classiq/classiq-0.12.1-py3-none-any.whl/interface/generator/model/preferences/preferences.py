import itertools
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

import networkx as nx
import pydantic
from pydantic.utils import sequence_like

from classiq.interface.backend.backend_preferences import BackendPreferences
from classiq.interface.generator.model.preferences.randomness import create_random_seed
from classiq.interface.generator.result import QuantumFormat
from classiq.interface.generator.transpiler_basis_gates import (
    DEFAULT_BASIS_GATES,
    DEFAULT_ROUTING_BASIS_GATES,
    ROUTING_TWO_QUBIT_BASIS_GATES,
    TWO_QUBIT_GATES,
    TranspilerBasisGates,
)
from classiq.interface.helpers.custom_pydantic_types import pydanticNonNegIntTuple

if TYPE_CHECKING:
    pydanticConstrainedQuantumFormatList = List[QuantumFormat]
else:
    pydanticConstrainedQuantumFormatList = pydantic.conlist(
        QuantumFormat, min_items=1, max_items=len(QuantumFormat)
    )


DEFAULT_DRAW_AT_LEVEL = 1
ConnectivityMap = List[pydanticNonNegIntTuple]

BACKEND_VALIDATION_ERROR_MESSAGE = (
    "Backend service provider and backend name should be specified together."
)
UNLIMITED_WIDTH = -1


class CustomHardwareSettings(pydantic.BaseModel):

    basis_gates: List[TranspilerBasisGates] = pydantic.Field(
        default=list(),
        description="The basis gates of the hardware. "
        "This set will be used during the model optimization. "
        "If none given, use default values: "
        f"If no connectivity map is given or the connectivity map is symmetric - {DEFAULT_BASIS_GATES}. "
        f"If a non-symmetric connectivity map is given - {DEFAULT_ROUTING_BASIS_GATES}. ",
    )
    connectivity_map: Optional[ConnectivityMap] = pydantic.Field(
        default=None,
        description="Qubit connectivity map, in the form [ [q0, q1], [q1, q2],...]. "
        "If none given, assume the hardware is fully connected",
    )
    is_symmetric_connectivity: bool = pydantic.Field(
        default=True,
        description="Assumes that the coupling map forms an undirected graph, "
        "so for every qubit pair [q0, q1], both qubits can act as control and target. "
        "If false, the first / second qubit denotes the control / target, respectively",
    )
    _width: int = pydantic.PrivateAttr(default=UNLIMITED_WIDTH)

    @pydantic.validator("connectivity_map")
    def validate_connectivity_map(cls, connectivity_map):
        if connectivity_map is None:
            return connectivity_map
        if not connectivity_map:
            raise ValueError("Connectivity map cannot be empty")
        if not _is_connected_map(connectivity_map):
            raise ValueError(
                f"Connectivity map must be connected: {connectivity_map} is not connected."
            )
        connectivity_map = _reindex_qubits(connectivity_map)
        return connectivity_map

    @pydantic.root_validator()
    def symmetrize_connectivity_map(cls, values):
        connectivity_map = values.get("connectivity_map")
        if connectivity_map is None:
            return values

        is_symmetric = values.get("is_symmetric_connectivity")
        if not is_symmetric:
            return values

        values["connectivity_map"] = _symmetrize_connectivity_map(connectivity_map)
        return values

    @pydantic.root_validator()
    def validate_basis_gates(cls, values):
        connectivity_map = values.get("connectivity_map")
        specified_basis_gates = values.get("basis_gates")
        if connectivity_map is None:
            values["basis_gates"] = specified_basis_gates or list(DEFAULT_BASIS_GATES)
            return values

        is_symmetric_connectivity = values.get("is_symmetric")
        if is_symmetric_connectivity or _check_symmetry(connectivity_map):
            values["basis_gates"] = specified_basis_gates or list(DEFAULT_BASIS_GATES)
            return values

        values["basis_gates"] = specified_basis_gates or list(
            DEFAULT_ROUTING_BASIS_GATES
        )
        invalid_gates = [
            gate
            for gate in specified_basis_gates
            if gate in TWO_QUBIT_GATES and gate not in ROUTING_TWO_QUBIT_BASIS_GATES
        ]
        if invalid_gates:
            raise ValueError(
                "Connectivity-aware synthesis with non-symmetric coupling map "
                "is currently supported for the following two-qubit gates only: cx, ecr, rzx."
            )

        return values

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._width: int = (
            len(set(itertools.chain.from_iterable(self.connectivity_map)))
            if self.connectivity_map
            else UNLIMITED_WIDTH
        )

    @property
    def width(self) -> int:
        return self._width

    def to_connectivity_graph(self) -> Optional[nx.DiGraph]:
        if self.connectivity_map is None:
            return None
        connectivity_graph = nx.DiGraph()
        connectivity_graph.add_edges_from(
            [tuple(pair) for pair in self.connectivity_map]
        )
        return connectivity_graph


def _is_connected_map(connectivity_map: ConnectivityMap) -> bool:
    connectivity_graph = nx.Graph()
    connectivity_graph.add_edges_from([tuple(pair) for pair in connectivity_map])
    return nx.is_connected(connectivity_graph)


def _reindex_qubits(connectivity_map: ConnectivityMap) -> ConnectivityMap:
    qubits = sorted(set(q for pair in connectivity_map for q in pair))
    return [(qubits.index(pair[0]), qubits.index(pair[1])) for pair in connectivity_map]


def _check_symmetry(connectivity_map: ConnectivityMap) -> bool:
    undirected_edges = set(tuple(sorted(edge)) for edge in connectivity_map)
    return len(undirected_edges) == len(connectivity_map) / 2


def _symmetrize_connectivity_map(connectivity_map: ConnectivityMap) -> ConnectivityMap:
    # A more complicated implementation than using set to maintain the order
    connectivity_map_no_duplicates = []
    for edge in connectivity_map:
        reversed_edge = (edge[1], edge[0])
        if (
            edge not in connectivity_map_no_duplicates
            and reversed_edge not in connectivity_map_no_duplicates
        ):
            connectivity_map_no_duplicates.append(edge)
    reversed_connectivity_map = [
        (edge[1], edge[0]) for edge in connectivity_map_no_duplicates
    ]
    return connectivity_map_no_duplicates + reversed_connectivity_map


class TranspilationOption(str, Enum):
    NONE = "none"
    DECOMPOSE = "decompose"
    OPTIMIZE = "optimize"


class Preferences(pydantic.BaseModel):

    _backend_preferences: Optional[BackendPreferences] = pydantic.PrivateAttr(
        default=None
    )
    backend_service_provider: Optional[str] = pydantic.Field(
        default=None, description="Provider company or cloud for the requested backend."
    )
    backend_name: Optional[str] = pydantic.Field(
        default=None, description="Name of the requested backend or target."
    )
    custom_hardware_settings: CustomHardwareSettings = pydantic.Field(
        default_factory=CustomHardwareSettings,
        description="Custom hardware settings which will be used during optimization. "
        "This field is ignored if backend preferences are given.",
    )
    output_format: pydanticConstrainedQuantumFormatList = pydantic.Field(
        default=[QuantumFormat.QASM],
        description="The quantum circuit output format(s). "
        "When multiple formats are requested, only the first one will be presented in "
        "the VSCode extension.",
    )

    pretty_qasm: bool = pydantic.Field(
        True,
        description="Prettify the OpenQASM2 outputs (use line breaks inside the gate "
        "declarations).",
    )

    qasm3: bool = pydantic.Field(
        False,
        description="Output OpenQASM 3.0 instead of OpenQASM 2.0. Relevant only for "
        "the `qasm` and `transpiled_qasm` attributes of `GeneratedCircuit`.",
    )

    draw_image: Optional[bool] = pydantic.Field(
        default=None,
        description="Determine whether the generation result will include an image of "
        "the circuit. If None, an image will be created if the circuit is not too big.",
    )

    draw_as_functions: Optional[bool] = pydantic.Field(
        default=None,
        description="If true, the generation output will be "
        "visualized as functions and not as an unrolled circuit",
    )

    draw_at_level: pydantic.PositiveInt = pydantic.Field(
        default=DEFAULT_DRAW_AT_LEVEL,
        description="If `draw_as_functions` is `True`, this specifies the hierarchy level of the functions that are "
        "shown in the visualization",
    )

    transpilation_option: TranspilationOption = pydantic.Field(
        default=TranspilationOption.OPTIMIZE,
        description="If true, the returned result will contain a "
        "transpiled circuit and its depth",
    )

    timeout_seconds: pydantic.PositiveInt = pydantic.Field(
        default=300, description="Generation timeout in seconds"
    )

    random_seed: int = pydantic.Field(
        default_factory=create_random_seed,
        description="The random seed used for the generation",
    )

    class Config:
        extra = "forbid"

    @pydantic.validator("output_format", pre=True, always=True)
    def validate_output_format(cls, output_format):
        if not sequence_like(output_format):
            return [output_format]

        if len(output_format) == len(set(output_format)):
            return output_format

        raise ValueError(
            f"output_format={output_format}\n"
            "has at least one format that appears twice or more"
        )

    @pydantic.root_validator()
    def validate_backend(cls, values):
        backend_name = values.get("backend_name")
        backend_service_provider = values.get("backend_service_provider")
        if (backend_name is None) != (backend_service_provider is None):
            raise ValueError(BACKEND_VALIDATION_ERROR_MESSAGE)
        return values

    @property
    def backend_preferences(self) -> Optional[BackendPreferences]:
        if self.backend_name is None or self.backend_service_provider is None:
            return None
        if self._backend_preferences is None:
            self._backend_preferences = BackendPreferences(
                backend_name=self.backend_name,
                backend_service_provider=self.backend_service_provider,
            )
        return self._backend_preferences
