from collections import OrderedDict
from typing import Dict
from typing import List


def convert_raw_policy_to_present(hub, policy: Dict, tags: List = None):
    """
    Convert organization policy response to a common format

    Args:
        policy: organization policy response from aws
        tags: list of tags attached to policy

    Returns:
        A dictionary of organization policy
    """
    translated_resource = {}
    describe_parameters = OrderedDict(
        {
            "Name": "name",
            "Description": "description",
            "Type": "policy_type",
            "Content": "content",
            "Id": "resource_id",
            "Arn": "arn",
            "AwsManaged": "aws_managed",
        }
    )

    for camel_case_key, snake_case_key in describe_parameters.items():
        if policy["PolicySummary"].get(camel_case_key) is not None:
            translated_resource[snake_case_key] = policy["PolicySummary"].get(
                camel_case_key
            )
        elif policy.get(camel_case_key) is not None:
            translated_resource[snake_case_key] = policy.get(camel_case_key)
    if tags:
        translated_resource["tags"] = tags
    return translated_resource


def convert_raw_organization_to_present(hub, organization: Dict, idem_name: str = None):
    """
    Convert the aws organization response to a common format

    Args:
        organization: describe organization response
        idem_name: Name of the resource

    Returns:
        A dictionary of organization
    """
    resource_id = organization.get("Id")
    translated_resource = {
        "name": idem_name if idem_name else resource_id,
        "resource_id": resource_id,
    }
    describe_parameters = OrderedDict(
        {
            "Arn": "arn",
            "MasterAccountArn": "master_account_arn",
            "MasterAccountId": "master_account_id",
            "MasterAccountEmail": "master_account_email",
            "FeatureSet": "feature_set",
            "AvailablePolicyTypes": "available_policy_types",
        }
    )

    if not "FeatureSet" in organization:
        organization["FeatureSet"] = "ALL"

    for camel_case_key, snake_case_key in describe_parameters.items():
        if organization.get(camel_case_key) is not None:
            translated_resource[snake_case_key] = organization.get(camel_case_key)
    return translated_resource


def convert_raw_ou_to_present(hub, ou: Dict, parent_id: str = None):
    """
    Convert organization policy response to a common format

    Args:
        ou: organization unit response from aws
        parent_id: id of the root

    Returns:
        A dictionary of organization unit
    """
    translated_resource = {"resource_id": ou.get("Id")}
    if ou.get("Name"):
        translated_resource["name"] = ou.get("Name")
    if parent_id:
        translated_resource["parent_id"] = parent_id

    if ou.get("Tags"):
        translated_resource["tags"] = ou.get("Tags")
    return translated_resource


def convert_raw_account_to_present(
    hub, parent_id: str = None, account: Dict = None, tags: Dict = None
):
    """
    Convert account response to a common format

    Args:
        hub: required for functions in hub
        parent_id: id of the account parent
        account: Account response from AWS
        tags: Tags of account

    Returns:
        A dictionary of account
    """
    describe_parameters = OrderedDict(
        {
            "Email": "email",
            "Arn": "arn",
            "Status": "status",
        }
    )
    resource_translated = {
        "name": account.get("Name"),
        "resource_id": account.get("Id"),
    }

    if parent_id:
        resource_translated["parent_id"] = parent_id
    for parameter_raw, parameter_present in describe_parameters.items():
        if parameter_raw in account:
            resource_translated[parameter_present] = account.get(parameter_raw)
    if tags:
        resource_translated["tags"] = tags
    return resource_translated
