from typing import Dict, List
import celery
import ewoks
from ewokscore import task_discovery
from ..config import configure_app

app = celery.Celery("ewoks")
configure_app(app)


@app.task(bind=True)
def execute_workflow(self, *args, execinfo=None, **kwargs) -> Dict:
    if execinfo is None:
        execinfo = dict()
    if "job_id" not in execinfo:
        execinfo["job_id"] = self.request.id
    return ewoks.execute_graph(*args, execinfo=execinfo, **kwargs)


@app.task()
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))
