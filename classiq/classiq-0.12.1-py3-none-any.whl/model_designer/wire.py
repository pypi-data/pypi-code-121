from typing import Optional

from classiq.interface.generator import function_call

from classiq.exceptions import ClassiqWiringError


class Wire:
    _start_call: Optional[function_call.FunctionCall] = None
    _start_name: Optional[str] = None
    _end_call: Optional[function_call.FunctionCall] = None

    def __init__(
        self,
        start_call: Optional[function_call.FunctionCall] = None,
        output_name: str = "",
    ) -> None:
        self.connect_wire_start(start_call=start_call, output_name=output_name)  # type: ignore[arg-type]

    def _initialize_wire_name(self, wire_name: Optional[str] = None) -> None:
        if wire_name is not None:
            self.wire_name = wire_name
        elif self.is_started:
            self.wire_name = f"{self._start_call.name}_{self._start_name}"  # type: ignore[union-attr]
        else:
            self.wire_name = ""

    def connect_wire_start(
        self, start_call: function_call.FunctionCall, output_name: str
    ) -> None:
        if self.is_started:
            raise ClassiqWiringError(
                "Cannot connect wire-start to an already started wire."
            )

        self._start_call: function_call.FunctionCall = start_call
        self._start_name: str = output_name

        self._initialize_wire_name()

    def connect_wire_end(
        self, end_call: function_call.FunctionCall, input_name: str
    ) -> None:
        if self.is_connected:
            raise ClassiqWiringError("Wire already connected")

        self._end_call: function_call.FunctionCall = end_call
        self._end_name: str = input_name

        end_call.inputs_dict[input_name] = self.wire_name
        end_call.non_zero_input_wires.append(self.wire_name)

        if self._start_call is not None:
            self.set_as_output(self.wire_name)

    def set_as_output(self, output_wire_name: str) -> None:
        if not self.is_started:
            raise ClassiqWiringError("Wire initialized incorrectly")
        if self.is_connected:
            raise ClassiqWiringError("Wire already connected")
        if self._start_name is None:
            raise ClassiqWiringError("Wire start name is uninitialized")

        self._start_call.outputs_dict[self._start_name] = output_wire_name  # type: ignore[union-attr]
        self._start_call.non_zero_output_wires.append(output_wire_name)  # type: ignore[union-attr]

    @property
    def is_connected(self) -> bool:
        return self.is_started and self.is_ended

    @property
    def is_started(self) -> bool:
        return self._start_call is not None

    @property
    def is_ended(self) -> bool:
        return (self._end_call is not None) and (
            self.is_started and self._start_name in self._start_call.outputs  # type: ignore[union-attr]
        )
