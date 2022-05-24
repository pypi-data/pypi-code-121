# AristaFlow REST Libraries
# Third Party Libraries
from af_org_model_manager.api.policy_resolution_api import PolicyResolutionApi
from af_org_model_manager.models.qa_remote_iterator_data import QaRemoteIteratorData
from af_org_model_manager.api.model_explorer_api import ModelExplorerApi

# Aristaflow Libraries
from aristaflow.abstract_service import AbstractService
from aristaflow.utils import OrgUtils


class OrgModelService(AbstractService):
    """
    Helper methods for accessing the organizational model
    """

    def get_qualified_agent(self, agent_id: int, org_pos_id: int):
        """
        Returns the qualified agent object for the given IDs
        """
        pr: PolicyResolutionApi = self._service_provider.get_service(
            PolicyResolutionApi
        )
        it: QaRemoteIteratorData = pr.resolve_policy(
            org_policy=OrgUtils.build_staff_assignment_rule_for_agent(
                agent_id, org_pos_id
            )
        )
        return it.agents[0]
    
    def get_agent_details(self, agent_name: str):
        """
        Returns the agent object for the given name
        """
        me: ModelExplorerApi = self._service_provider.get_service(
            ModelExplorerApi
        )
        return me.get_agent_for_user_name(agent_name)