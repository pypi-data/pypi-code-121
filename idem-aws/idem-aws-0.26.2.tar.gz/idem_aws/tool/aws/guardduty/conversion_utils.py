from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions to convert raw resource state from AWS GUARDDUTY to present input format.
"""


async def convert_raw_detector_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    detector_describe = {}
    resource_parameters = OrderedDict(
        {"FindingPublishingFrequency": "finding_publishing_frequency"}
    )
    ret = await hub.exec.boto3.client.guardduty.list_detectors(ctx)
    for detector_id in ret["ret"]["DetectorIds"]:
        resource_id = detector_id
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    if raw_resource and raw_resource["result"] is True:
        detector_describe = raw_resource["ret"]

    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource["ret"]:
            resource_translated[parameter_present] = raw_resource["ret"].get(
                parameter_raw
            )
    data_sources_new = hub.tool.aws.guardduty.detector_utils.render_data_sources(
        detector_describe
    )

    if detector_describe["Tags"]:
        resource_translated["tags"] = dict(detector_describe["Tags"])

    resource_translated["enable"] = True

    if detector_describe["DataSources"]:
        resource_translated["data_sources"] = data_sources_new
    return resource_translated
