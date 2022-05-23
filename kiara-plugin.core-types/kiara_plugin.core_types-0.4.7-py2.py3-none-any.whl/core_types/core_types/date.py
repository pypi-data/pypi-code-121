# -*- coding: utf-8 -*-
import datetime
from typing import Any, Dict, Optional

from kiara import KiaraModule
from kiara.exceptions import KiaraProcessingException
from kiara.models.values.value import ValueMap
from kiara.modules import ValueSetSchema


class ExtractDateModule(KiaraModule):
    """Extract a date object from a string."""

    _module_type_name = "date.extract_from_string"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        return {"text": {"type": "string", "doc": "The input string."}}

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "date": {"type": "date", "doc": "The date extracted from the input string."}
        }

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        from dateutil import parser

        text = inputs.get_value_data("text")
        # date_match = re.findall(r"_(\d{4}-\d{2}-\d{2})_", text)
        # assert date_match
        # d_obj = parser.parse(date_match[0])  # type: ignore
        d_obj = parser.parse(text)

        outputs.set_value("date", d_obj)


class DateRangeCheckModule(KiaraModule):
    """Check whether a date falls within a specified date range.

    If none one of the inputs 'earliest' or 'latest' is set, this module will always return 'True'.

    Return ``True`` if that's the case, otherwise ``False``.
    """

    _module_type_name = "date.check_range"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        inputs: Dict[str, Dict[str, Any]] = {
            "date": {"type": "date", "doc": "The date to check."},
            "earliest": {
                "type": "date",
                "doc": "The earliest date that is allowed.",
                "optional": True,
            },
            "latest": {
                "type": "date",
                "doc": "The latest date that is allowed.",
                "optional": True,
            },
        }

        return inputs

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        outputs = {
            "within_range": {
                "type": "boolean",
                "doc": "A boolean indicating whether the provided date was within the allowed range ('true'), or not ('false')",
            }
        }
        return outputs

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        d: datetime.datetime = inputs.get_value_data("date")
        earliest: Optional[datetime.datetime] = inputs.get_value_data("earliest")
        latest: Optional[datetime.datetime] = inputs.get_value_data("latest")

        if not earliest and not latest:
            outputs.set_value("within_range", True)
            return

        if not isinstance(d, datetime.datetime):
            raise KiaraProcessingException(f"Invalid format for input date: {type(d)}")

        if earliest and latest:
            matches = earliest <= d <= latest
        elif earliest:
            matches = earliest <= d
        else:
            matches = d <= latest  # type: ignore

        outputs.set_value("within_range", matches)
