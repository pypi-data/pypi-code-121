# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Placeholder object for code generation."""


class PlaceholderObject:
    """Placeholder object to be used when overriding an object representation in some other data structure."""
    def __init__(self, repr_str: str):
        self.repr_str = repr_str

    def __repr__(self) -> str:
        return self.repr_str
