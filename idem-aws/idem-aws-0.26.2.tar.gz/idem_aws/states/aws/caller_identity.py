import copy
from collections import OrderedDict
from typing import Any
from typing import Dict


async def search(hub, ctx, name) -> Dict[str, Any]:
    """
    Details about the IAM user or role whose credentials are used to call the operation.

    Args:
        name(string): An Idem name of the resource.

    Request Syntax:
        [Idem-resource-state-name]:
          aws.caller_identity.search:
          - name: 'string'

    Examples:

            my-caller-account:
              aws.caller_identity.search:
                - name: value

    Response Syntax:
          {
            name: 'string',
            user_id: 'string',
            account_id: 'string',
            arn: 'string'
          }

    Response Structure:
        name(string): An Idem name of the resource.
        user_id(string): The unique identifier of the calling entity.
        account_id(string): AWS account ID number of the account that owns or contains the calling entity.
        arn(string): AWS ARN associated with the calling entity.

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    ret = await hub.exec.boto3.client.sts.get_caller_identity(ctx)
    if not ret["result"]:
        result["result"] = False
        result["comment"] = ret["comment"]
        return result
    resource_parameters = OrderedDict(
        {"UserId": "user_id", "Account": "account_id", "Arn": "arn"}
    )
    resource_translated = {"name": name}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in ret["ret"]:
            resource_translated[parameter_present] = ret["ret"][parameter_raw]
    result["old_state"] = resource_translated
    result["new_state"] = copy.deepcopy(result["old_state"])
    return result
