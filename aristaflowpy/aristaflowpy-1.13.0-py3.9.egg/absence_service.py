# -*- coding: utf-8 -*-
# Default Python Libraries
from datetime import datetime
from typing import List

# AristaFlow REST Libraries
from af_org_model_manager.api.policy_resolution_api import PolicyResolutionApi
from af_org_model_manager.api.qa_remote_iterator_api import QaRemoteIteratorApi
from af_worklist_manager.api.poss_abs_remote_iterator_api import PossAbsRemoteIteratorApi
from af_worklist_manager.api.worklist_update_manager_api import WorklistUpdateManagerApi
from af_worklist_manager.models.absence_data import AbsenceData
from af_worklist_manager.models.absence_information import AbsenceInformation
from af_worklist_manager.models.qualified_agent import QualifiedAgent
from aristaflow.abstract_service import AbstractService
from aristaflow.utils import FROM_BPM_DATE, TO_BPM_DATE, OrgUtils


class ExtendedAbsenceInformation(object):
    """Absence information providing additional and typed data."""

    absence_information: AbsenceInformation = None
    absentee: QualifiedAgent = None
    is_absent_now = False
    substitute_summary = ""
    substitute_agents: List[QualifiedAgent] = []
    absent_from: datetime = None
    absent_until: datetime = None

    def __init__(
        self,
        absentee: QualifiedAgent,
        is_absent_now: bool,
        substitute_summary: str,
        substitute_agents: List[QualifiedAgent],
        ai: AbsenceInformation,
    ):
        self.is_absent_now = is_absent_now
        self.substitute_summary = substitute_summary
        self.substitute_agents = substitute_agents
        self.absentee = absentee
        if ai:
            self.absent_from = FROM_BPM_DATE(ai.from_date)
            self.absent_until = FROM_BPM_DATE(ai.to_date)
            self.absence_information = ai


class AbsenceService(AbstractService):
    """
    Helper methods for implementing absences and substitutions
    """

    def get_possible_absentees(self) -> List[QualifiedAgent]:
        """Returns the possible absentees"""
        wum: WorklistUpdateManagerApi = self._service_provider.get_service(WorklistUpdateManagerApi)
        return self._rem_iter_handler.consume(
            wum.get_possible_absentees(),
            "agents",
            PossAbsRemoteIteratorApi,
            PossAbsRemoteIteratorApi.poss_abs_get_next,
        )

    def get_absence_information(
        self, *qas: List[QualifiedAgent]
    ) -> List[ExtendedAbsenceInformation]:
        """Returns the absence information for the given agents, or for all agents if no agent is provided"""
        wum: WorklistUpdateManagerApi = self._service_provider.get_service(WorklistUpdateManagerApi)
        pol_res: PolicyResolutionApi = self._service_provider.get_service(PolicyResolutionApi)
        if qas is None or len(qas) == 0:
            qas = self.get_possible_absentees()

        res: List[ExtendedAbsenceInformation] = []
        for absentee in qas:
            ai: AbsenceInformation = wum.get_absence_information(body=absentee)
            is_absent_now = False
            substitute_summary = ""
            substitute_agents = []
            if ai is not None:
                unix_millis_now = TO_BPM_DATE(datetime.utcnow())
                # from date not in the future
                absence_started = ai.from_date < unix_millis_now
                absence_lasting = ai.to_date == 0 or ai.to_date > unix_millis_now
                is_absent_now = absence_started and absence_lasting
                if ai.substitution_rule:
                    substitute_agents = self._rem_iter_handler.consume(
                        pol_res.resolve_policy(org_policy=ai.substitution_rule),
                        "agents",
                        QaRemoteIteratorApi,
                    )
                substitute_summary = OrgUtils.summarize_qa_list(*substitute_agents)
            else:
                ai = {}
            res.append(
                ExtendedAbsenceInformation(
                    absentee, is_absent_now, substitute_summary, substitute_agents, ai
                )
            )
        return res

    def is_absent_now(self, absent_from: datetime = None, absent_until: datetime = None) -> bool:
        """Returns whether the specified absence range is considered as absent now."""
        unix_millis_now = TO_BPM_DATE(datetime.utcnow())
        from_date = TO_BPM_DATE(absent_from)
        to_date = TO_BPM_DATE(absent_until)
        absence_started = from_date < unix_millis_now
        absence_lasting = to_date == 0 or to_date > unix_millis_now
        return absence_started and absence_lasting

    def create_substitutes_staff_assignment_rule(self, qas: List[QualifiedAgent]) -> str:
        """Creates a staff assignment rule selecting the given agents as substitutes for someone."""
        if len(qas) == 0:
            # not set FIXME check API
            return ""
        sar = ""
        for qa in qas:
            qa_sar = self.create_staff_assignment_rule_for_qa(qa)
            if sar == "":
                sar = qa_sar
            else:
                sar = sar + " OR " + qa_sar
        return sar

    def create_staff_assignment_rule_for_qa(self, qa: QualifiedAgent) -> str:
        """Creates a staff assignment rule selecting exactly the given agent."""
        return OrgUtils.build_staff_assignment_rule_for_agent(qa.agent_id, qa.org_pos_id)

    def set_absent(
        self,
        absentee: QualifiedAgent,
        substitutes: List[QualifiedAgent],
        absent_from: datetime = None,
        absent_until: datetime = None,
    ):
        """Sets the given agent as absent using the proved information"""
        wum: WorklistUpdateManagerApi = self._service_provider.get_service(WorklistUpdateManagerApi)
        _from = TO_BPM_DATE(absent_from)
        to = TO_BPM_DATE(absent_until)
        substitution_rule = self.create_substitutes_staff_assignment_rule(substitutes)
        absence_data = AbsenceData(absentee, _from, to, substitution_rule)
        wum.set_absent(body=absence_data)

    def set_present(self, absentee: QualifiedAgent):
        """Sets the agent present"""
        wum: WorklistUpdateManagerApi = self._service_provider.get_service(WorklistUpdateManagerApi)
        wum.set_present(body=absentee)

    def drop_absence(self, absentee: QualifiedAgent):
        """Drops any current or future absence"""
        wum: WorklistUpdateManagerApi = self._service_provider.get_service(WorklistUpdateManagerApi)
        wum.drop_absence(body=absentee)
