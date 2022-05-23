# -*- coding: utf-8 -*-
import time

from kiara import KiaraModule
from kiara.models.module import KiaraModuleConfig
from kiara.models.values.value import ValueMap
from kiara.modules import ValueSetSchema
from pydantic import Field


class LogicProcessingModuleConfig(KiaraModuleConfig):
    """Config class for all the 'logic'-related modules."""

    # this is used to simulate longer running jobs
    delay: float = Field(
        default=0,
        description="the delay in seconds from processing start to when the output is returned.",
    )


class LogicProcessingModule(KiaraModule):

    _config_cls = LogicProcessingModuleConfig


class NotModule(LogicProcessingModule):
    """Negates the input."""

    _module_type_name = "logic.not"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:
        """The not module only has one input, a boolean that will be negated by the module."""

        return {
            "a": {"type": "boolean", "doc": "A boolean describing this input state."}
        }

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:
        """The output of this module is a single boolean, the negated input."""

        return {
            "y": {
                "type": "boolean",
                "doc": "A boolean describing the module output state.",
            }
        }

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:
        """Negates the input boolean."""

        time.sleep(self.config.get("delay"))  # type: ignore

        outputs.set_value("y", not inputs.get_value_data("a"))


class AndModule(LogicProcessingModule):
    """Returns 'True' if both inputs are 'True'."""

    _module_type_name = "logic.and"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:
        return {
            "a": {"type": "boolean", "doc": "A boolean describing this input state."},
            "b": {"type": "boolean", "doc": "A boolean describing this input state."},
        }

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:
        return {
            "y": {
                "type": "boolean",
                "doc": "A boolean describing the module output state.",
            }
        }

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        time.sleep(self.config.delay)  # type: ignore

        outputs.set_value(
            "y", inputs.get_value_data("a") and inputs.get_value_data("b")
        )


class OrModule(LogicProcessingModule):
    """Returns 'True' if one of the inputs is 'True'."""

    _module_type_name = "logic.or"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "a": {"type": "boolean", "doc": "A boolean describing this input state."},
            "b": {"type": "boolean", "doc": "A boolean describing this input state."},
        }

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "y": {
                "type": "boolean",
                "doc": "A boolean describing the module output state.",
            }
        }

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        time.sleep(self.config.get("delay"))  # type: ignore
        outputs.set_value("y", inputs.get_value_data("a") or inputs.get_value_data("b"))
