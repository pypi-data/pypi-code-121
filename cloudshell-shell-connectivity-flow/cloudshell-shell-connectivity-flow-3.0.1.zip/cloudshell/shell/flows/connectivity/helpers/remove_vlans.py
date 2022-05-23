from copy import deepcopy
from itertools import chain, groupby
from typing import Iterable, List

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
    ConnectivityTypeEnum,
)


def _grouped_actions(
    actions: Iterable[ConnectivityActionModel],
) -> List[List[ConnectivityActionModel]]:
    def key_fn(action):
        return (
            action.action_target.name,
            action.custom_action_attrs.vm_uuid,
            action.custom_action_attrs.vnic,
        )

    return [
        list(grouped_actions)
        for _, grouped_actions in groupby(sorted(actions, key=key_fn), key=key_fn)
    ]


def prepare_remove_vlan_actions(
    set_actions: Iterable[ConnectivityActionModel],
    remove_actions: Iterable[ConnectivityActionModel],
) -> List[ConnectivityActionModel]:
    """Preparing actions for remove VLAN method.

    If action type is setVlan we need to clear VLANs on that interface.
    """
    actions = []
    for grouped_actions in _grouped_actions(chain(set_actions, remove_actions)):
        if any(a.type is ConnectivityTypeEnum.SET_VLAN for a in grouped_actions):
            copy_action = deepcopy(next(iter(grouped_actions)))
            copy_action.connection_params.vlan_id = ""
            # we don't need to clear port for the Cloud Providers
            if not copy_action.custom_action_attrs.vm_uuid:
                actions.append(copy_action)
        else:
            actions.extend(grouped_actions)
    return actions
