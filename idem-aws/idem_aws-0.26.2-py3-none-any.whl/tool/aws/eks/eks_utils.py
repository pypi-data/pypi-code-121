from typing import Any
from typing import Dict

from dict_tools import differ


def get_resource_vpc_config_changes(
    hub, old_vpc_config: Dict, new_vpc_config: Dict
) -> Dict[str, Any]:
    """
    Returns updated resource vpc config changes

     Args:
        hub: required for functions in hub
        old_vpc_config(Dict): old resource vpc config changes
        new_vpc_config(Dict): new resource vpc config changes

    Returns: A dict with resource vpc config changes
    """
    final_vpc_config = {}
    if new_vpc_config.get(
        "endpointPrivateAccess"
    ) is not None and not old_vpc_config.get(
        "endpointPrivateAccess"
    ) == new_vpc_config.get(
        "endpointPrivateAccess"
    ):
        final_vpc_config["endpointPrivateAccess"] = new_vpc_config.get(
            "endpointPrivateAccess"
        )

    if new_vpc_config.get(
        "endpointPublicAccess"
    ) is not None and not old_vpc_config.get(
        "endpointPublicAccess"
    ) == new_vpc_config.get(
        "endpointPublicAccess"
    ):
        final_vpc_config["endpointPublicAccess"] = new_vpc_config.get(
            "endpointPublicAccess"
        )

    if new_vpc_config.get("publicAccessCidrs") and not old_vpc_config.get(
        "publicAccessCidrs"
    ) == new_vpc_config.get("publicAccessCidrs"):
        final_vpc_config["publicAccessCidrs"] = new_vpc_config.get("publicAccessCidrs")
    return final_vpc_config


def update_labels(old_labels: dict, new_labels: dict) -> Dict[str, Any]:
    """
    Returns updated labels used in update node group config

     Args:
        old_labels(Dict): old labels
        new_labels(Dict): new labels

    Returns: A dict with labels
    """
    labels_to_add = {}
    labels_to_remove = []
    for key, value in new_labels.items():
        if (key in old_labels and old_labels.get(key) != new_labels.get(key)) or (
            key not in old_labels
        ):
            labels_to_add[key] = value

    for key in old_labels:
        if key not in new_labels:
            labels_to_remove.append(key)

    final_labels = {}
    if labels_to_add:
        final_labels["addOrUpdateLabels"] = labels_to_add
    if labels_to_remove:
        final_labels["removeLabels"] = labels_to_remove
    return final_labels


def update_taints(old_taints: list, new_taints: list) -> Dict[str, Any]:
    """
    Returns updated taints used in update node group config

     Args:
        old_taints(list): old taints
        new_taints(list): new taints

    Returns: A dict with taints
    """
    taints_to_add = list()
    taints_to_remove = list()
    old_taints_map = {taint.get("key"): taint for taint in old_taints or []}
    if new_taints is not None:
        for tag in new_taints:
            if tag.get("key") in old_taints_map:
                if tag.get("value") != old_taints_map.get(tag.get("key")).get("value"):
                    taints_to_add.append(tag)
                del old_taints_map[tag.get("key")]
            else:
                taints_to_add.append(tag)
        taints_to_remove = [taint for taint in old_taints_map.values()]
    final_taints = {}
    if taints_to_add:
        final_taints["addOrUpdateTaints"] = taints_to_add
    if taints_to_remove:
        final_taints["removeTaints"] = taints_to_remove

    return final_taints


def get_updated_node_group_config(
    hub,
    old_node_group_config: Dict,
    labels: dict,
    taints: list,
    scaling_config: Dict,
    update_config: Dict,
) -> Dict[str, Any]:
    """
    Returns updated node group config

     Args:
        hub: required for functions in hub
        old_node_group_config(Dict): old node group config
        labels(dict): new labels
        taints(List): new taints
        scaling_config(Dict): new scaling config
        update_config(Dict): new update config

    Returns: A dict with node group config
    """
    final_node_group_config = {}
    current_labels = update_labels(old_node_group_config.get("labels"), labels)
    if current_labels:
        final_node_group_config["labels"] = current_labels
    current_taints = update_taints(old_node_group_config.get("taints"), taints)
    if current_taints:
        final_node_group_config["taints"] = current_taints
    if differ.deep_diff(old_node_group_config.get("scaling_config"), scaling_config):
        final_node_group_config["scaling_config"] = scaling_config
    if differ.deep_diff(old_node_group_config.get("update_config"), update_config):
        final_node_group_config["update_config"] = update_config
    return final_node_group_config
