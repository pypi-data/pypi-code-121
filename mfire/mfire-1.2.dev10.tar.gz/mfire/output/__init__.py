"""mfire.output module

This module handles everything related to the output

"""
from mfire.output.base import BaseOutputProduction
from mfire.output.adapters import OutputAdapter


__all__ = ["OutputAdapter", "BaseOutputProduction"]
