#
#  Copyright 2021 Simple Machines Pty Ltd - All Rights Reserved.
#
#  This file is part of Anaml.
#
#  Unauthorized copying and/or distribution of this file, via any medium
#  is strictly prohibited.
#

"""Exceptions for the Anaml client."""

from __future__ import annotations

import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class Reason:
    """One reason that an error has been reported."""

    message: str
    field: typing.Optional[str] = None

    def __str(self):
        """Format the reason for display."""
        if self.field is not None:
            return f"{self.message} ({self.field})"
        else:
            return self.message

    @staticmethod
    def from_json(data: dict) -> Reason:
        """Parse a reason from JSON."""
        return Reason(
            data['message'],
            data.get('field', None)
        )


@dataclasses.dataclass
class AnamlError(Exception):
    """An application error reported by Anaml."""

    message: str = "The Anaml server reported an error"
    errors: typing.List[Reason] = dataclasses.field(default_factory=list)

    def __str__(self):
        """String formatting for the error report."""
        if len(self.errors) > 0:
            return f"{self.message}: {', '.join([str(r) for r in self.errors])}"
        else:
            return self.message

    @staticmethod
    def from_json(data: dict) -> AnamlError:
        """Parse an AnamlError from a JSON error report."""
        return AnamlError(
            errors=[
                Reason.from_json(reason) for reason in data["errors"]
            ]
        )
