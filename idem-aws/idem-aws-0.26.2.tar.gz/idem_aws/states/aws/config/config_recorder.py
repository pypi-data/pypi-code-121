import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    role_arn: str,
    recording_group: Dict,
    recording: bool = False,
    resource_id: str = None,
) -> Dict[str, Any]:
    """
    Creates a new configuration recorder to record the selected resource configurations, please see AWS Config services
    Args:
        name(Text): The name of the recorder.
        role_arn (Text): Amazon Resource Name (ARN) of the IAM role used to describe the Amazon Web Services resources associated with the account.
        recording_group (Dict): Specifies the types of Amazon Web Services resources for which Config records configuration changes.
        recording (Bool, Optional): Specifies recording status of the configuration recorder. Default is False.
        resource_id (Text, Optional): The name of the recorder.

    Request syntax:
        [aws-config-recorder]:
          aws.config.config_recorder.present:
          - name: 'string'
          - resource_id: 'string'
          - role_arn 'string'
          - recording: 'string'
          - recording_group: 'dict'

    Returns:
         Dict[str, Any]

    Examples:
        .. code-block:: sls
            aws-config-recorder:
              aws.config.config_recorder.present:
                - name: 'config_recorder'
                - resource_id: 'config_recorder'
                - role_arn 'arn:aws:iam::012345678912:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig'
                - recording: true
                - recording_group:
                    allSupported: false
                    includeGlobalResourceTypes: false
                    resourceTypes:
                    - "AWS::ApiGateway::Stage"

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated: bool = False
    only_recording_status_changed: bool = False

    if resource_id:
        resource = await hub.exec.boto3.client.config.describe_configuration_recorders(
            ctx,
            ConfigurationRecorderNames=[name],
        )
        if not resource["result"]:
            result["comment"] = resource["comment"]
            result["result"] = False
            return result
        else:
            before = resource["ret"]["ConfigurationRecorders"][0]

    if before:
        before_recording_status = (
            await hub.exec.boto3.client.config.describe_configuration_recorder_status(
                ctx,
                ConfigurationRecorderNames=[name],
            )
        )
        if not before_recording_status["result"]:
            result["comment"] = before_recording_status["comment"]
            result["result"] = False
            return result
        before["recording"] = before_recording_status["ret"][
            "ConfigurationRecordersStatus"
        ][0]["recording"]

        resource_translated = await hub.tool.aws.config.conversion_utils.convert_raw_config_recorder_to_present(
            ctx,
            raw_resource=before,
            recording=before_recording_status["ret"]["ConfigurationRecordersStatus"][0][
                "recording"
            ],
        )
        result["old_state"] = resource_translated
        resource_updated = await hub.tool.aws.config.config_utils.is_resource_updated(
            before=resource_translated,
            role_arn=role_arn,
            recording_group=recording_group,
        )
        if not resource_updated and resource_translated["recording"] == recording:
            result["comment"] = (f"aws.config.config_recorder '{name}' already exists",)
            result["new_state"] = copy.deepcopy(result["old_state"])
            return result

        if not resource_updated and resource_translated["recording"] != recording:
            only_recording_status_changed = True

    if ctx.get("test", False):
        result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
            enforced_state={},
            desired_state={
                "name": name,
                "role_arn": role_arn,
                "recording": recording,
                "resource_id": resource_id,
                "recording_group": recording_group,
            },
        )
        operation = (
            "update"
            if before
            and (resource_updated or resource_translated["recording"] != recording)
            else "create"
        )
        result["comment"] = (f"Would {operation} aws.config.config_recorder '{name}'",)
        return result

    if not only_recording_status_changed:
        update_ret = await hub.exec.boto3.client.config.put_configuration_recorder(
            ctx=ctx,
            ConfigurationRecorder={
                "name": name,
                "roleARN": role_arn,
                "recordingGroup": recording_group,
            },
        )
        if not update_ret["result"]:
            result["comment"] = update_ret["comment"]
            result["result"] = False
            return result

        after_ret = await hub.exec.boto3.client.config.describe_configuration_recorders(
            ctx,
            ConfigurationRecorderNames=[name],
        )
        if not after_ret["result"]:
            result["comment"] = after_ret["comment"]
            result["result"] = False
            return result

        result[
            "new_state"
        ] = await hub.tool.aws.config.conversion_utils.convert_raw_config_recorder_to_present(
            ctx,
            raw_resource=after_ret["ret"]["ConfigurationRecorders"][0],
            recording=None,
        )
        operation = "Created" if not before else "Updated"
        result["comment"] = (f"{operation} aws.config.config_recorder '{name}'",)
    else:
        result["new_state"] = copy.deepcopy(result["old_state"])

    # If it is create recorder case and recording is True
    #   OR
    # If it is update recorder case and recording status is changed
    if (not before and recording) or (before and recording != before["recording"]):
        if recording:
            recording_status_ret = (
                await hub.exec.boto3.client.config.start_configuration_recorder(
                    ctx=ctx, ConfigurationRecorderName=name
                )
            )
        else:
            recording_status_ret = (
                await hub.exec.boto3.client.config.stop_configuration_recorder(
                    ctx=ctx, ConfigurationRecorderName=name
                )
            )
        if not recording_status_ret["result"]:
            result["comment"] = recording_status_ret["comment"]
            result["result"] = False
            return result

        after_recording_status_ret = (
            await hub.exec.boto3.client.config.describe_configuration_recorder_status(
                ctx,
                ConfigurationRecorderNames=[name],
            )
        )
        if not after_recording_status_ret["result"]:
            result["comment"] = after_recording_status_ret["comment"]
            result["result"] = False
            return result
        result["new_state"]["recording"] = after_recording_status_ret["ret"][
            "ConfigurationRecordersStatus"
        ][0]["recording"]
        if only_recording_status_changed:
            result["comment"] = hub.tool.aws.comment_utils.update_comment(
                resource_type="aws.config.config_recorder", name=name
            )
    else:
        if not before:
            result["new_state"]["recording"] = False
        else:
            result["new_state"]["recording"] = before["recording"]
    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    """
    Deletes the configuration recorder. After the configuration recorder is deleted,
    Config will not record resource configuration changes until you create a new configuration recorder.

    Args:
        name(Text): The name of the recorder.
        resource_id(Text, optional): AWS Config configuration recorder Name. Idem automatically considers this resource being absent
         if this field is not specified.

    Returns:
          Dict[str, Any]

    Examples:
          .. code-block:: sls

            aws-config-recorder:
              aws.config.config_recorder.present:
                - name: 'config_recorder'
                - resource_id: 'config_recorder'

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    if resource_id:
        resource = await hub.exec.boto3.client.config.describe_configuration_recorders(
            ctx,
            ConfigurationRecorderNames=[name],
        )
        if not resource["result"]:
            if "NoSuchConfigurationRecorderException" in str(resource["comment"]):
                result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
                    resource_type="aws.config.config_recorder", name=name
                )
                return result
            result["comment"] = resource["comment"]
            result["result"] = False
            return result
        else:
            before = resource["ret"]["ConfigurationRecorders"][0]

    if before:
        before_recording = (
            await hub.exec.boto3.client.config.describe_configuration_recorder_status(
                ctx,
                ConfigurationRecorderNames=[name],
            )
        )
        if not before_recording["result"]:
            result["comment"] = before_recording["comment"]
            result["result"] = False
            return result

        translated_resource = await hub.tool.aws.config.conversion_utils.convert_raw_config_recorder_to_present(
            ctx,
            raw_resource=before,
            recording=before_recording["ret"]["ConfigurationRecordersStatus"][0][
                "recording"
            ],
        )
        result["old_state"] = translated_resource
    else:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.config.config_recorder", name=name
        )
        return result

    if ctx.get("test", False):
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.config.config_recorder", name=name
        )
        return result
    else:
        delete_ret = await hub.exec.boto3.client.config.delete_configuration_recorder(
            ctx, ConfigurationRecorderName=name
        )
        result["result"] = delete_ret["result"]
        if not result["result"]:
            result["comment"] = delete_ret["comment"]
            return result
        result["comment"] = hub.tool.aws.comment_utils.delete_comment(
            resource_type="aws.config.config_recorder", name=name
        )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    """
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Return details about your config recorder.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.config.config_recorder
    """
    result = {}
    ret = await hub.exec.boto3.client.config.describe_configuration_recorders(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe configuration recorder {ret['comment']}")
        return {}

    for resource in ret["ret"]["ConfigurationRecorders"]:
        name = resource["name"]
        recording_status = (
            await hub.exec.boto3.client.config.describe_configuration_recorder_status(
                ctx,
                ConfigurationRecorderNames=[name],
            )
        )
        if not recording_status["result"]:
            hub.log.warning(
                f"Could not fetch configuration recorder '{name}' status with error {recording_status['comment']}"
            )
            continue

        recorder_name = f"{name}-config-recorder"
        translated_resource = await hub.tool.aws.config.conversion_utils.convert_raw_config_recorder_to_present(
            ctx,
            raw_resource=resource,
            recording=recording_status["ret"]["ConfigurationRecordersStatus"][0][
                "recording"
            ],
        )
        result[recorder_name] = {
            "aws.config.config_recorder.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in translated_resource.items()
            ]
        }
    return result
