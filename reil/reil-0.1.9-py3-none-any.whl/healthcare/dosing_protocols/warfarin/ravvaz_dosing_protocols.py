# -*- coding: utf-8 -*-
'''
AAA, CAA, PGAA, PGPGA, PGPGI classes
====================================

Study arms in `Ravvaz et al. (2017)
<https://doi.org/10.1161/circgenetics.117.001804>`_
'''

from typing import Any, Dict

from reil.healthcare.dosing_protocols.dosing_protocol import DosingDecision
from reil.healthcare.dosing_protocols.three_phase_dosing_protocol import \
    ThreePhaseDosingProtocol
from reil.healthcare.dosing_protocols.warfarin.aurora import Aurora
from reil.healthcare.dosing_protocols.warfarin.intermountain import \
    Intermountain
from reil.healthcare.dosing_protocols.warfarin.iwpc import IWPC
from reil.healthcare.dosing_protocols.warfarin.lenzini import Lenzini


class AAA(ThreePhaseDosingProtocol):
    '''
    A composite dosing protocol with `Aurora` in all phases.
    '''

    def __init__(self) -> None:
        aurora_instance = Aurora()
        super().__init__(aurora_instance, aurora_instance, aurora_instance)

    def prescribe(
            self, patient: Dict[str, Any]) -> DosingDecision:
        dosing_decision, self._additional_info = \
            self._initial_protocol.prescribe(patient, self._additional_info)

        return dosing_decision

    def __repr__(self) -> str:
        return super().__repr__() + '[AAA]'


class CAA(ThreePhaseDosingProtocol):
    '''
    A composite dosing protocol with clinical `IWPC` in the initial phase
    (days 1 and 2), and `Aurora` in the adjustment and maintenance phases.
    '''

    def __init__(self) -> None:
        iwpc_instance = IWPC('clinical')
        aurora_instance = Aurora()
        super().__init__(iwpc_instance, aurora_instance, aurora_instance)

    def prescribe(
            self, patient: Dict[str, Any]) -> DosingDecision:
        day: int = patient['day']
        if day <= 2:
            temp, self._additional_info = self._initial_protocol.prescribe(
                patient, self._additional_info)
            dosing_decision = DosingDecision(temp.dose, 3 - day)
        else:
            dosing_decision, self._additional_info = \
                self._adjustment_protocol.prescribe(
                    patient, self._additional_info)

        return dosing_decision

    def __repr__(self) -> str:
        return super().__repr__() + '[CAA]'


class PGAA(ThreePhaseDosingProtocol):
    '''
    A composite dosing protocol with pharmacogenetic `IWPC` in the initial
    phase (days 1 and 2), and `Aurora` in the adjustment and maintenance
    phases.
    '''

    def __init__(self) -> None:
        iwpc_instance = IWPC('pharmacogenetic')
        aurora_instance = Aurora()
        super().__init__(iwpc_instance, aurora_instance, aurora_instance)

    def prescribe(
            self, patient: Dict[str, Any]) -> DosingDecision:
        day: int = patient['day']
        if day <= 2:
            temp, self._additional_info = self._initial_protocol.prescribe(
                patient, self._additional_info)
            dosing_decision = DosingDecision(temp.dose, 3 - day)
        else:
            dosing_decision, self._additional_info = \
                self._adjustment_protocol.prescribe(
                    patient, self._additional_info)

        return dosing_decision

    def __repr__(self) -> str:
        return super().__repr__() + '[PGAA]'


class PGPGA(ThreePhaseDosingProtocol):
    '''
    A composite dosing protocol with modified `IWPC` in the initial phase
    (days 1, 2, and 3), `Lenzini` in the adjustment phase (days 4 and 5),
    and `Aurora` in the maintenance phase.
    '''

    def __init__(self) -> None:
        iwpc_instance = IWPC('modified')
        lenzini_instance = Lenzini()
        aurora_instance = Aurora()
        super().__init__(iwpc_instance, lenzini_instance, aurora_instance)

    def prescribe(
            self, patient: Dict[str, Any]) -> DosingDecision:
        if patient['day'] <= 3:
            temp, self._additional_info = \
                self._initial_protocol.prescribe(
                    patient, self._additional_info)
            dosing_decision = DosingDecision(temp.dose, 4 - patient['day'])
        elif patient['day'] <= 5:
            temp, self._additional_info = \
                self._adjustment_protocol.prescribe(
                    patient, self._additional_info)
            dosing_decision = DosingDecision(temp.dose, 6 - patient['day'])
        else:
            dosing_decision, self._additional_info = \
                self._maintenance_protocol.prescribe(
                    patient, self._additional_info)

        return dosing_decision

    def __repr__(self) -> str:
        return super().__repr__() + '[PGPGA]'


class PGPGI(ThreePhaseDosingProtocol):
    '''
    A composite dosing protocol with modified `IWPC` in the initial phase
    (days 1, 2, and 3), `Lenzini` in the adjustment phase (days 4 and 5),
    and `Intermountain` in the maintenance phase.
    '''

    def __init__(self) -> None:
        iwpc_instance = IWPC('modified')
        lenzini_instance = Lenzini()
        intermountain_instance = Intermountain(enforce_day_ge_8=False)
        super().__init__(
            iwpc_instance, lenzini_instance, intermountain_instance)

    def prescribe(
            self, patient: Dict[str, Any]) -> DosingDecision:
        if patient['day'] <= 3:
            temp, self._additional_info = \
                self._initial_protocol.prescribe(
                    patient, self._additional_info)
            dosing_decision = DosingDecision(temp.dose, 4 - patient['day'])
        elif patient['day'] <= 5:
            temp, self._additional_info = \
                self._adjustment_protocol.prescribe(
                    patient, self._additional_info)
            dosing_decision = DosingDecision(temp.dose, 6 - patient['day'])
        else:
            dosing_decision, self._additional_info = \
                self._maintenance_protocol.prescribe(
                    patient, self._additional_info)

        return dosing_decision

    def __repr__(self) -> str:
        return super().__repr__() + '[PGPGI]'
