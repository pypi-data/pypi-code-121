from typing import Iterable, Optional, Union

import pydantic
from typing_extensions import Literal

from classiq.interface.chemistry.ground_state_problem import GroundStateProblem
from classiq.interface.generator import function_params

_EXCITATIONS_DICT = {"s": 1, "d": 2, "t": 3, "q": 4}


class UCC(function_params.FunctionParams):
    """
    Ucc ansatz
    """

    gs_problem: Union[
        Literal["ground_state_problem"], GroundStateProblem
    ] = pydantic.Field(description="Ground state problem object describing the system.")
    use_naive_evolution: bool = pydantic.Field(
        default=False, description="Whether to evolve the operator naively"
    )
    excitations: Union[int, Iterable[int], Iterable[str], str] = pydantic.Field(
        default_factory=lambda: [1, 2],
        description="type of excitation operators in the UCC ansatz",
    )
    max_depth: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="Maximum depth of the generated quantum circuit ansatz",
    )

    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    @pydantic.validator("excitations")
    def validate_excitations(cls, excitations):
        if isinstance(excitations, int):
            if excitations not in _EXCITATIONS_DICT.values():
                raise ValueError(
                    f"possible values of excitations are {list(_EXCITATIONS_DICT.values())}"
                )
            excitations = [excitations]

        elif isinstance(excitations, Iterable):
            excitations = list(set(excitations))
            if all(isinstance(i, int) for i in excitations):
                if not all(i in _EXCITATIONS_DICT.values() for i in excitations):
                    raise ValueError(
                        f"possible values of excitations are {list(_EXCITATIONS_DICT.values())}"
                    )

            elif all(isinstance(i, str) for i in excitations):
                if not all(i in _EXCITATIONS_DICT.keys() for i in excitations):
                    raise ValueError(
                        f"possible values of excitations are {list(_EXCITATIONS_DICT.keys())}"
                    )
                excitations = sorted([_EXCITATIONS_DICT[i] for i in excitations])

            else:
                raise ValueError(
                    "excitations must be of the same type (all str or all int)"
                )
        return excitations
