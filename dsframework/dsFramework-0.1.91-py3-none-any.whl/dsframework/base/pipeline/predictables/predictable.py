#!/usr/bin/env python
# coding: utf-8

"""! @brief ZIDS_Predictable base class."""

from typing import Any
from dsframework.base.common import ZIDS_Object


class ZIDS_Predictable(ZIDS_Object):
    """! ZIDS_Predictable base class for a single predictable object."""

    def __init__(self) -> None:
        """! Initializer for ZIDS_Predictable
        Initializes local class variables, those ZIDS_Predictable variables will be transferred from component to
        component in the pipeline as an input and output.
        """
        ##
        # @hidecallgraph @hidecallergraph
        super().__init__()
        self.name: str = ''
        self.input: Any = None
        self.target: Any = None
        self.pred: Any = None
        self.prob: float = -1.0
        self.forced_pred: Any = None
        self.forced_reason: str = 'Did Not Force'
