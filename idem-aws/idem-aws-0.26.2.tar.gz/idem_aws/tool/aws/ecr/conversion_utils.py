from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List

"""
Util functions to convert raw resource state from AWS ECR to present input format.
"""


def convert_raw_repository_to_present(
    hub, raw_resource: Dict[str, Any], tags: List = None, idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("repositoryName")
    resource_parameters = OrderedDict(
        {
            "repositoryArn": "repository_arn",
            "registryId": "registry_id",
            "repositoryName": "repository_name",
            "repositoryUri": "repository_uri",
            "imageTagMutability": "image_tag_mutability",
            "imageScanningConfiguration": "image_scanning_configuration",
            "encryptionConfiguration": "encryption_configuration",
        }
    )

    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource and raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    if tags:
        resource_translated["tags"] = tags

    return resource_translated


def convert_raw_repository_policy_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    r"""
    Convert AWS ECR Repository Policy response to a common idem present state

    Args:
        hub: required for functions in hub
        raw_resource(Dict[str, Any]): The AWS response to convert.
        idem_resource_name(string, optional): An Idem name of the resource.

    Returns:
        Dict[str, Any]: Common idem present state
    """

    resource_id = (
        f"{raw_resource.get('registryId')}-{raw_resource.get('repositoryName')}"
    )
    resource_parameters = OrderedDict(
        {
            "registryId": "registry_id",
            "repositoryName": "repository_name",
        }
    )
    resource_translated = {
        "name": idem_resource_name if idem_resource_name else resource_id,
        "resource_id": resource_id,
    }

    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource and raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    if raw_resource.get("policyText"):
        resource_translated[
            "policy_text"
        ] = hub.tool.aws.state_comparison_utils.standardise_json(
            raw_resource.get("policyText")
        )

    return resource_translated
