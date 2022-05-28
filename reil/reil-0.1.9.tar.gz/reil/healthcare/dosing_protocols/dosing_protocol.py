# -*- coding: utf-8 -*-
'''
DosingProtocol class
====================

The base class for all basic dosing protocols.
'''

import dataclasses
from typing import Any, Dict, Optional, Tuple


@dataclasses.dataclass
class DosingDecision:
    dose: float
    duration: Optional[int] = None


AdditionalInfo = Dict[str, Any]


class DosingProtocol:
    '''
    Base class for all dosing protocol objects.
    '''

    def __init__(self) -> None:
        pass

    def prescribe(self,
                  patient: Dict[str, Any],
                  additional_info: AdditionalInfo
                  ) -> Tuple[DosingDecision, AdditionalInfo]:
        '''
        Prescribe a dose for the given `patient` and `additional_info`.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics necessary to make dosing
            decisions.

        additional_info:
            A dictionary of information being communicated between protocols at
            each call to `prescribe`. These additional information are
            protocol-dependent.

        Returns
        -------
        :
            A `DosingDecision` along with updated `additional_info`.
        '''
        raise NotImplementedError

    def reset(self) -> None:
        '''Reset the dosing protocol'''
        pass
