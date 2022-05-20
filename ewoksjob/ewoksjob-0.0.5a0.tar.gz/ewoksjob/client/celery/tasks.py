from celery.execute import send_task
from celery.result import AsyncResult
from ..test_workflow import test_workflow

__all__ = ["trigger_workflow", "trigger_test_workflow", "discover_tasks_from_modules"]


def trigger_workflow(**kwargs) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.execute_workflow", **kwargs)


def trigger_test_workflow(seconds=0) -> AsyncResult:
    return trigger_workflow(
        args=(test_workflow(),),
        kwargs={"inputs": [{"id": "sleepnode", "name": 0, "value": seconds}]},
    )


def discover_tasks_from_modules(**kwargs) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.discover_tasks_from_modules", **kwargs)
