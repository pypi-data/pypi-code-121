# -*- coding: utf-8 -*-
import re
import typing

from kiara import KiaraModule
from kiara.exceptions import KiaraProcessingException
from kiara.models.module import KiaraModuleConfig
from kiara.models.values.value import ValueMap
from kiara.modules import ValueSetSchema
from pydantic import Field


class RegexModuleConfig(KiaraModuleConfig):

    regex: str = Field(description="The regex to apply.")
    only_first_match: bool = Field(
        description="Whether to only return the first match, or all matches.",
        default=False,
    )


class RegexModule(KiaraModule):
    """Match a string using a regular expression."""

    _config_cls = RegexModuleConfig
    _module_type_name = "string.match_regex"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:
        return {"text": {"type": "string", "doc": "The text to match."}}

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        if self.get_config_value("only_first_match"):
            output_schema = {"text": {"type": "string", "doc": "The first match."}}
        else:
            raise NotImplementedError()

        return output_schema

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        text = inputs.get_value_data("text")
        regex = self.get_config_value("regex")
        matches = re.findall(regex, text)

        if not matches:
            raise KiaraProcessingException(f"No match for regex: {regex}")

        if self.get_config_value("only_first_match"):
            result = matches[0]
        else:
            result = matches

        outputs.set_value("text", result)


class ReplaceModuleConfig(KiaraModuleConfig):

    replacement_map: typing.Dict[str, str] = Field(
        description="A map, containing the strings to be replaced as keys, and the replacements as values."
    )
    default_value: typing.Optional[str] = Field(
        description="The default value to use if the string to be replaced is not in the replacement map. By default, this just returns the string itself.",
        default=None,
    )


class ReplaceStringModule(KiaraModule):
    """Replace a string if it matches a key in a mapping dictionary."""

    _config_cls = ReplaceModuleConfig
    _module_type_name = "string.replace"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        return {"text": {"type": "string", "doc": "The input string."}}

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:
        return {"text": {"type": "string", "doc": "The replaced string."}}

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        text = inputs.get_value_data("text")
        repl_map = self.get_config_value("replacement_map")
        default = self.get_config_value("default_value")

        if text not in repl_map.keys():
            if default is None:
                result = text
            else:
                result = default
        else:
            result = repl_map[text]

        outputs.set_value("text", result)
