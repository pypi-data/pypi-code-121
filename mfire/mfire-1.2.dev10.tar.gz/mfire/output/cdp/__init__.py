"""mfire.output.cdp module

This module handles everything related to the cdp

"""
from mfire.output.cdp.periods import CDPPeriod
from mfire.output.cdp.datasets import CDPDataset
from mfire.output.cdp.components import (
    CDPAlea,
    CDPText,
    CDPComponents,
)
from mfire.output.cdp.productions import CDPProduction
from mfire.output.cdp.adapters import CDPRiskAdapter, CDPTextAdapter


__all__ = [
    "CDPPeriod",
    "CDPDataset",
    "CDPAlea",
    "CDPText",
    "CDPComponents",
    "CDPProduction",
    "CDPRiskAdapter",
    "CDPTextAdapter",
]
