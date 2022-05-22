from typing import Dict, Iterable, List, Set, Type

from classiq.interface.generator.function_call import FunctionCall, IOName
from classiq.interface.generator.functions import FunctionData

from classiq.exceptions import ClassiqWiringError
from classiq.model_designer import function_handler, wire

_SAME_INPUT_NAME_ERROR_MSG: str = "Cannot create multiple inputs with the same name"


class CompositeFunctionInputWire(wire.Wire):
    def __init__(self, input_name: IOName) -> None:
        super().__init__()
        self._initialize_wire_name(wire_name=input_name)

    @property
    def is_ended(self) -> bool:
        return self._end_call is not None


class CompositeFunctionOutputWire(wire.Wire):
    @property
    def is_ended(self) -> bool:
        return self.is_started and self._start_name in self._start_call.outputs  # type: ignore[union-attr]


class CompositeFunctionGenerator(function_handler.FunctionHandler):
    def __init__(self, function_name: str) -> None:
        super().__init__()
        self._name = function_name
        self._logic_flow_list: List[FunctionCall] = list()
        self._input_names: Set[IOName] = set()
        self._generated_inputs: Dict[IOName, wire.Wire] = dict()
        self._generated_outputs: Dict[IOName, wire.Wire] = dict()

    @property
    def _logic_flow(self) -> List[FunctionCall]:
        return self._logic_flow_list

    @property
    def _output_wire_type(self) -> Type[wire.Wire]:
        return CompositeFunctionOutputWire

    def create_inputs(
        self, input_names: Iterable[IOName]
    ) -> Dict[IOName, CompositeFunctionInputWire]:
        wire_dict = {}

        for name in input_names:
            if name in wire_dict:
                raise ClassiqWiringError(_SAME_INPUT_NAME_ERROR_MSG)
            wire_dict[name] = CompositeFunctionInputWire(input_name=name)

        self._update_generated_wires(wires=wire_dict.values())
        if any(name in self._generated_inputs for name in wire_dict):
            raise ClassiqWiringError(_SAME_INPUT_NAME_ERROR_MSG)
        self._generated_inputs.update(wire_dict)

        return wire_dict

    def set_outputs(self, outputs: Dict[IOName, CompositeFunctionOutputWire]) -> None:
        self._verify_legal_wires(wires=outputs.values())

        for output_name, output_wire in outputs.items():
            if isinstance(output_wire, CompositeFunctionInputWire):
                raise ClassiqWiringError(
                    f"Can't connect input directly to output {output_name}"
                )
            output_wire.set_as_output(output_wire_name=output_wire.wire_name)
            self._generated_outputs[output_name] = output_wire

    def to_function_data(self) -> FunctionData:
        inputs = {name: wire.wire_name for name, wire in self._generated_inputs.items()}
        outputs = {
            name: wire.wire_name for name, wire in self._generated_outputs.items()
        }
        return FunctionData(
            name=self._name, logic_flow=self._logic_flow, inputs=inputs, outputs=outputs
        )
