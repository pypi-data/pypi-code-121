from collections import OrderedDict
from typing import Any
from typing import Dict

from dict_tools import differ


async def compare_inputs_and_update_lambda_function(
    hub,
    ctx,
    name: str,
    function: Dict[str, Any],
    update: Dict[str, Any],
    code: Dict[str, Any],
    resource_id: str,
    plan_state: Dict[str, Any],
    timeout: Dict = None,
):
    """
    Updates a Lambda function's code. If code signing is enabled for the function, the code package must be signed by
    a trusted publisher. The function's code is locked when you publish a version. You can't modify the code of a
    published version, only the unpublished version.

    Modify the version-specific settings of a Lambda function. When you update a function, Lambda provisions an
    instance of the function and its supporting resources. If your function connects to a VPC, this process can take
    a minute. During this time, you can't modify the function, but you can still invoke it. Updates the configuration
    for asynchronous invocation for a function, version, or alias.

    Update function's code, configuration, function's event invoke config This function compares data with new params
    and invokes update actions with appropriate arguments.

    Args:
        plan_state: idem --test state for update on AWS Lambda.
        name: The name of the Lambda function.
        update: a dictionary with newly passed values of params.
        function: response returned by describe on a lambda function
        code: a dictionary detailing existing code config.
        resource_id: The name/ ARN/ partial ARN of the AWS Lambda function, version, or alias.
        timeout(Dict, optional): Timeout configuration for create/update/deletion of AWS Lambda Function.
            * update (string) -- Timeout configuration for updating AWS Lambda Function
                * delay -- The amount of time in seconds to wait between attempts.
                * max_attempts -- Customized timeout configuration containing delay and max attempts.

    Returns:
        {"result": True|False, "comment": ("A tuple",), "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)

    if not ctx.get("test", False):
        image_uri = None
        if code:
            image_uri = code.get("ImageUri")

        old_code_details = {
            "FunctionName": function.get("FunctionName"),
            "Architectures": function.get("Architectures"),
            "RevisionId": function.get("RevisionId"),
            "ImageUri": image_uri,
        }
        new_code_details = {
            "FunctionName": update.get("FunctionName"),
            "Architectures": update.get("Architectures"),
            "RevisionId": update.get("RevisionId"),
            "ImageUri": update.get("ImageUri"),
        }

        diff_in_code = differ.deep_diff(old_code_details, new_code_details)

        try:
            if diff_in_code.get("new"):
                publish = update.get("Publish", False)
                update_function_code = await hub.exec.boto3.client[
                    "lambda"
                ].update_function_code(
                    ctx=ctx,
                    FunctionName=resource_id,
                    ZipFile=update.get("ZipFile"),
                    S3Bucket=update.get("S3Bucket"),
                    S3Key=update.get("S3Key"),
                    S3ObjectVersion=update.get("S3ObjectVersion"),
                    ImageUri=diff_in_code.get("new").get("ImageUri"),
                    Publish=publish,
                    DryRun=False,
                    RevisionId=diff_in_code.get("new").get("RevisionId")
                    if diff_in_code.get("new").get("RevisionId")
                    else function.get("RevisionId"),
                    Architectures=diff_in_code.get("new").get("Architectures"),
                )
                result["result"] = result["result"] and update_function_code["result"]
                result["comment"] = result["comment"] + update_function_code["comment"]
                if not result["result"]:
                    return result

                waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                    default_delay=1,
                    default_max_attempts=20,
                    timeout_config=timeout.get("update") if timeout else None,
                )
                hub.log.debug(f"Waiting on updating aws.lambda.function '{name}'")
                try:
                    await hub.tool.boto3.client.wait(
                        ctx,
                        "lambda",
                        "function_updated",
                        FunctionName=resource_id,
                        WaiterConfig=waiter_config,
                    )
                except Exception as e:
                    result["comment"] = result["comment"] + (str(e),)
                    result["result"] = False

            update_function_config = await hub.exec.boto3.client[
                "lambda"
            ].update_function_configuration(
                ctx=ctx,
                FunctionName=resource_id,
                Role=update.get("Role"),
                Handler=update.get("Handler"),
                Description=update.get("Description"),
                Timeout=update.get("Timeout"),
                MemorySize=update.get("MemorySize"),
                VpcConfig=update.get("VpcConfig"),
                Environment=update.get("Environment"),
                Runtime=update.get("Runtime"),
                DeadLetterConfig=update.get("DeadLetterConfig"),
                KMSKeyArn=update.get("KMSKeyArn"),
                TracingConfig=update.get("TracingConfig"),
                RevisionId=update.get("RevisionId"),
                Layers=update.get("Layers"),
                FileSystemConfigs=update.get("FileSystemConfigs"),
                ImageConfig=update.get("ImageConfig"),
            )

            result["result"] = result["result"] and update_function_config.get("result")
            result["comment"] = result["comment"] + update_function_config["comment"]

            if not result["result"]:
                return result

            waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                default_delay=1,
                default_max_attempts=20,
                timeout_config=timeout.get("update") if timeout else None,
            )
            hub.log.debug(f"Waiting on updating aws.lambda.function '{name}'")
            try:
                await hub.tool.boto3.client.wait(
                    ctx,
                    "lambda",
                    "function_updated",
                    FunctionName=resource_id,
                    WaiterConfig=waiter_config,
                )
            except Exception as e:
                result["comment"] = result["comment"] + (str(e),)
                result["result"] = False
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    else:
        update_params = OrderedDict(
            {
                "name": update.get("FunctionName"),
                "role": update.get("Role"),
                "code": update.get("Code"),
                "resource_id": update.get("FunctionName"),
                "runtime": update.get("Runtime"),
                "handler": update.get("Handler"),
                "description": update.get("Description"),
                "function_timeout": update.get("Timeout"),
                "memory_size": update.get("MemorySize"),
                "publish": update.get("Publish"),
                "vpc_config": update.get("VpcConfig"),
                "package_type": update.get("PackageType"),
                "dead_letter_config": update.get("DeadLetterConfig"),
                "environment": update.get("Environment"),
                "kms_key_arn": update.get("KMSKeyArn"),
                "tracing_config": update.get("TracingConfig"),
                "tags": update.get("Tags"),
                "layers": update.get("Layers"),
                "file_system_configs": update.get("FileSystemConfigs"),
                "image_config": update.get("ImageConfig"),
                "code_signing_config_arn": update.get("CodeSigningConfigArn"),
                "architectures": update.get("Architectures"),
                "qualifier": update.get("Qualifier"),
                "maximum_retry_attempts": update.get("MaximumRetryAttempts"),
                "maximum_event_age_in_seconds": update.get(
                    "maximum_event_age_in_seconds"
                ),
                "destination_config": update.get("DestinationConfig"),
                "revision_id": update.get("RevisionId"),
            }
        )
        for key, value in update_params.items():
            if value is None:
                if key not in plan_state:
                    plan_state[key] = None
            else:
                plan_state[key] = value
    return result
