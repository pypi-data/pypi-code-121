# -*- coding: utf-8 -*-
# Default Python Libraries
from typing import Dict, List, Union

# AristaFlow REST Libraries
from af_worklist_manager.api.del_rec_remote_iterator_api import DelRecRemoteIteratorApi
from af_worklist_manager.api.delegation_manager_api import DelegationManagerApi
from af_worklist_manager.models.delg_rec_with_comment import DelgRecWithComment
from af_worklist_manager.models.qa_initial_remote_iterator_data import QaInitialRemoteIteratorData
from af_worklist_manager.models.qa_remote_iterator_data import QaRemoteIteratorData
from af_worklist_manager.models.qualified_agent import QualifiedAgent
from af_worklist_manager.models.worklist_item import WorklistItem
from aristaflow.abstract_service import AbstractService


class DelegationService(AbstractService):
    """
    Helper methods for implementing delegation
    """

    def get_delegation_recipients(self, *items: WorklistItem) -> List[QualifiedAgent]:
        """Retrieves the possible delegation recipients for the given worklist items, ie.
        the intersection of all all possible delegation recipients of all items.
        """
        recipient_set: Dict[str, QualifiedAgent] = None
        for item in items:
            recs = self._get_delegation_recipients(item)
            rec: QualifiedAgent = None
            if recipient_set is None:
                # initial iteration: add what is there
                recipient_set = {}
                for rec in recs:
                    recipient_set[f"{rec.agent_id}_{rec.org_pos_id}"] = rec
            else:
                # not the initial iteration: remove what doesn't exist
                keys_to_delete: List[str] = []
                for added_rec_key in recipient_set:
                    added_rec = recipient_set[added_rec_key]
                    found = False
                    for rec in recs:
                        if (
                            rec.agent_id == added_rec.agent_id
                            and rec.org_pos_id == added_rec.org_pos_id
                        ):
                            found = True
                            break
                    if not found:
                        keys_to_delete.append(added_rec_key)
                # remove from target set all entries which are not found in the delegation
                # recipients of the current item_id
                for key_to_delete in keys_to_delete:
                    del recipient_set[key_to_delete]

            # empty intersection, no need to continue
            if len(recipient_set) == 0:
                break

        return recipient_set.values()

    def _get_delegation_recipients(self, item: WorklistItem) -> List[QualifiedAgent]:
        """Retrieves the possible delegation recipients for the given worklist item"""
        dm: DelegationManagerApi = self._service_provider.get_service(DelegationManagerApi)
        drec: QaInitialRemoteIteratorData = dm.get_delegation_recipients(item.id)
        recipients: List[QualifiedAgent] = []
        self._iterate_delegation_recipients(recipients, drec)
        return recipients

    def _iterate_delegation_recipients(
        self,
        recipients: List[QualifiedAgent],
        cur_iter: Union[QaInitialRemoteIteratorData, QaRemoteIteratorData],
    ):
        """Reads up the given delegation recipients iterator"""
        if cur_iter is None:
            return
        if cur_iter.agents:
            recipients += cur_iter.agents
        else:
            return
        if cur_iter.dropped:
            return

        api: DelRecRemoteIteratorApi = self._service_provider.get_service(DelRecRemoteIteratorApi)
        next_iter = api.del_rec_get_next(cur_iter.iterator_id)
        self._iterate_delegation_recipients(recipients, next_iter)

    def delegate(self, item: WorklistItem, comment: str, *args):
        """Delegates the given worklist item using the given comments to all QualifiedAgents supplied in *args
        :param List[QualifiedAgents] args: Delegation recipients
        """
        dm: DelegationManagerApi = self._service_provider.get_service(DelegationManagerApi)
        body: DelgRecWithComment = DelgRecWithComment(recipients=args, comment=comment)
        dm.delegate_work_item(body, item.id)
