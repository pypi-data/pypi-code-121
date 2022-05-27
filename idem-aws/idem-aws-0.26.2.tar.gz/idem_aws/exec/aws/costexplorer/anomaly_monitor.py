from typing import Any
from typing import Dict


async def update_monitor(
    hub, ctx, before: Dict[str, Any], monitor_name: str, monitor_arn: str
):
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}
    if monitor_name and before.get("MonitorName") != monitor_name:
        update_payload["MonitorName"] = monitor_name
    if update_payload:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.ce.update_anomaly_monitor(
                ctx=ctx, MonitorArn=monitor_arn, **update_payload
            )
            if not update_ret["result"]:
                result["comment"] = result["comment"] + update_ret["comment"]
                return result
        result["ret"] = {}
        if "MonitorName" in update_payload:
            result["ret"]["monitor_name"] = update_payload["MonitorName"]
            result["comment"] = result["comment"] + (
                f"Update monitor_name: {update_payload['MonitorName']}",
            )
    return result
