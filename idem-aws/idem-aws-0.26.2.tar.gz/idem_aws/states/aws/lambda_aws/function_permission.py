"""

hub.exec.boto3.client.lambda.add-permission
hub.exec.boto3.client.lambda.remove-permission
hub.exec.boto3.client.lambda.get-policy

"""
import copy
import json
from typing import Any
from typing import Dict

# if no permission exists it throws below error message.
PERMISSION_DOES_NOT_EXISTS = "ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the GetPolicy operation"


async def present(
    hub,
    ctx,
    name: str,
    action: str,
    function_name: str,
    principal: str,
    source_arn: str = None,
    source_account: str = None,
    resource_id: str = None,
) -> Dict[str, Any]:
    r"""

    Add specified permission to the lambda function.

    Args:
        hub:
        ctx:
        name(str): Name/Id of the statement/permission
        action(str): The action that the principal can use on the function. For example, lambda:InvokeFunction or
                lambda:GetFunction.
        function_name(str): The name of the Lambda function, version, or alias.
                        Name formats
                        Function name - my-function (name-only), my-function:v1 (with alias).
                        Function ARN - arn:aws:lambda:us-west-2:123456789012:function:my-function .
                        Partial ARN - 123456789012:function:my-function .
        principal(str): The Amazon Web Services service or account that invokes the function. If you specify a service,
                    use source_arn or source_account to limit who can invoke the function through that service.
        source_arn(str, Optional): For Amazon Web Services , the ARN of the Amazon Web Services resource that invokes the
                    function. For example, an Amazon S3 bucket or Amazon SNS topic.
        source_account(str, Optional): For Amazon S3, the ID of the account that owns the resource. Use this together with SourceArn to
                        ensure that the resource is owned by the specified account. It is possible for an Amazon S3
                        bucket to be deleted by its owner and recreated by another account.
        resource_id(str, Optional): Name/Id of the statement/permission



    Request Syntax:
        [statement_id]:
          aws.lambda_aws.function_permission.present:
          - name: 'string'
            resource_id: 'string'
            action: 'string'
            function_name: 'string'
            principal:
                'string' : 'string'

    Returns:
        Dict[str, Any]

    Examples:

        . code-block:: sls

            test-001:
              aws.lambda_aws.function_permission.present:
              - action: lambda:GetAlias
              - effect: Allow
              - function_name: ecd17a181d6588e27c976cdeff501e90750b0dcafebba907cc4aab3c
              - name: test-001
              - principal:
                  AWS: AIDAX2FJ77DC2AS7BAPBU
              - resource_id: test-001


    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    # check if lambda function exists
    ret = await hub.exec.boto3.client["lambda"].get_function(
        ctx, FunctionName=function_name
    )
    if not ret["result"]:
        result["comment"] = ret["comment"]
        result["result"] = False
        return result

    # get current set of permissions
    get_policy = await hub.exec.boto3.client["lambda"].get_policy(
        ctx, FunctionName=function_name
    )

    if not get_policy["result"] and not any(
        PERMISSION_DOES_NOT_EXISTS in msg for msg in get_policy["comment"]
    ):
        result["comment"] = get_policy["comment"]
        result["result"] = False
        return result

    if get_policy["result"]:
        final_resource_id = resource_id if resource_id else name
        raw_statements = json.loads(get_policy["ret"]["Policy"])["Statement"]

        for statement in raw_statements:
            if statement["Sid"] == final_resource_id:
                result[
                    "old_state"
                ] = hub.tool.aws.lambda_aws.conversion_utils.convert_raw_lambda_permission_to_present(
                    raw_resource=statement, function_name=function_name
                )
                result["comment"] = (
                    f"aws.lambda_aws.function_permission {final_resource_id} already exists",
                )
                result["new_state"] = copy.deepcopy(result["old_state"])
                return result

    if ctx.get("test", False):
        result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
            resource_type="aws.lambda_aws.function_permission", name=name
        )
        principal_response = {"AWS": principal}
        result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
            enforced_state={},
            desired_state={
                "name": name,
                "resource_id": name,
                "action": action,
                "function_name": function_name,
                "principal": principal_response,
            },
        )
        return result

    add_permission = await hub.exec.boto3.client["lambda"].add_permission(
        ctx,
        FunctionName=function_name,
        StatementId=name,
        Action=action,
        Principal=principal,
        SourceArn=source_arn,
        SourceAccount=source_account,
    )
    if not add_permission["result"]:
        result["comment"] = add_permission["comment"]
        result["result"] = False
        return result

    get_policy = await hub.exec.boto3.client["lambda"].get_policy(
        ctx, FunctionName=function_name
    )
    if not get_policy["result"]:
        result["comment"] = get_policy["comment"]
        result["result"] = False
        return result

    raw_statements = json.loads(get_policy["ret"]["Policy"])["Statement"]

    for statement in raw_statements:
        if statement["Sid"] == name:
            result[
                "new_state"
            ] = hub.tool.aws.lambda_aws.conversion_utils.convert_raw_lambda_permission_to_present(
                raw_resource=statement, function_name=function_name
            )
            break

    return result


async def absent(
    hub, ctx, name: str, function_name: str, resource_id: str = None
) -> Dict[str, Any]:
    r"""

    Remove specified permission from the lambda function.

    Args:
        hub:
        ctx:
        name(str): Name/Id of the statement/permission
        function_name(str): The name of the Lambda function, version, or alias.
                        Name formats
                        Function name - my-function (name-only), my-function:v1 (with alias).
                        Function ARN - arn:aws:lambda:us-west-2:123456789012:function:my-function .
                        Partial ARN - 123456789012:function:my-function .
        resource_id(str, Optional): Name/Id of the statement/permission

    Request Syntax:
        [statement_id]:
          aws.lambda_aws.function_permission.absent:
          - name: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        . code-block:: sls

            test-001:
              aws.lambda_aws.function_permission.absent:
              - name: test-001

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)

    ret = await hub.exec.boto3.client["lambda"].get_function(
        ctx, FunctionName=function_name
    )
    if not ret["result"]:
        result["comment"] = ret["comment"]
        result["result"] = False
        return result

    get_policy = await hub.exec.boto3.client["lambda"].get_policy(
        ctx, FunctionName=function_name
    )

    if not get_policy["result"]:
        if any(PERMISSION_DOES_NOT_EXISTS in msg for msg in get_policy["comment"]):
            result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
                resource_type="aws.lambda_aws.function_permission", name=resource_id
            )
        else:
            result["comment"] = ret["comment"]
            result["result"] = False
        return result

    raw_statements = json.loads(get_policy["ret"]["Policy"])["Statement"]

    list_of_statement_ids = [statement["Sid"] for statement in raw_statements]

    if name not in list_of_statement_ids:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.lambda_aws.function_permission", name=resource_id
        )
        return result

    for statement in raw_statements:
        if statement["Sid"] == name:
            result[
                "old_state"
            ] = hub.tool.aws.lambda_aws.conversion_utils.convert_raw_lambda_permission_to_present(
                raw_resource=statement, function_name=function_name
            )
            break

    if ctx.get("test", False):
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.lambda_aws.function_permission", name=resource_id
        )
        return result

    remove_permission = await hub.exec.boto3.client["lambda"].remove_permission(
        ctx,
        FunctionName=function_name,
        StatementId=resource_id if resource_id else name,
    )
    if not remove_permission["result"]:
        result["comment"] = remove_permission["comment"]
        result["result"] = False

    result["comment"] = hub.tool.aws.comment_utils.delete_comment(
        resource_type="aws.lambda_aws.function_permission", name=resource_id
    )

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""

    Returns permissions associated with each lambda function.

    Args:
        hub:
        ctx:

    Request Syntax:
        [statement-id]:
          aws.lambda_aws.function_permission.present:
          - name: 'string'
            resource_id: 'string'
            statements:
            - action: 'string'
              effect: 'string'
              principal:
                'string'
              statement_id: 'string'


    Returns:
        Dict[str, Any]

    Examples:

        . code-block:: sls

            test-001:
              aws.lambda_aws.function_permission.present:
              - name: test-001
                resource_id: test-001
                function_name: ecd17a181d6588e27c976cdeff501e90750b0dcafebba907cc4aab3c
                action: lambda:GetAlias
                effect: Allow
                principal:
                  AWS: arn:aws:iam::537227425989:user/idem-fixture-user-18964248-75dd-4765-80b2-100901a8c74e

    """

    result = {}

    ret = await hub.exec.boto3.client["lambda"].list_functions(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe lambda functions. Error: {ret['comment']}")
        return result

    if ret and ret["result"] and ret["ret"]["Functions"]:
        for function in ret["ret"]["Functions"]:
            function_name = function.get("FunctionName")
            get_policy = await hub.exec.boto3.client["lambda"].get_policy(
                ctx, FunctionName=function_name
            )
            if not get_policy["result"]:
                if not any(
                    PERMISSION_DOES_NOT_EXISTS in msg for msg in get_policy["comment"]
                ):
                    hub.log.debug(
                        f"Could not describe lambda functions permission for {function_name}. Error: {get_policy['comment']}"
                    )
                continue

            raw_statements = json.loads(get_policy["ret"]["Policy"])["Statement"]
            for statement in raw_statements:
                permission_translated = hub.tool.aws.lambda_aws.conversion_utils.convert_raw_lambda_permission_to_present(
                    raw_resource=statement, function_name=function_name
                )
                result[statement["Sid"]] = {
                    "aws.lambda_aws.function_permission.present": [
                        {parameter_key: parameter_value}
                        for parameter_key, parameter_value in permission_translated.items()
                    ]
                }

    return result
