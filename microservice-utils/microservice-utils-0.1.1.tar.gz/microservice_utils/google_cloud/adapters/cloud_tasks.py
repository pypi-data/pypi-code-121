import logging
from collections import namedtuple
from typing_extensions import NotRequired, TypedDict

import ulid
from google.cloud import tasks_v2

from microservice_utils.google_cloud.models import GcpProjectConfig

logger = logging.getLogger(__name__)


class OidcToken(TypedDict):
    audience: str
    service_account_email: NotRequired[str]


def extract_task_name_from_task_path(task_path: str) -> str:
    return task_path.split("/")[-1]


class TaskEnqueuer:
    def __init__(self, project: GcpProjectConfig):
        self._client = tasks_v2.CloudTasksClient()
        self._project = project

    def get_queue_path(self, queue: str) -> str:
        return self._client.queue_path(self._project.id, self._project.region, queue)

    def get_task_path(self, queue: str, task_name: str) -> str:
        return self._client.task_path(
            self._project.id, self._project.region, queue, task_name
        )

    def enqueue_http_request(
        self,
        url: str,
        queue: str,
        payload: bytes,
        task_name: str = None,
        oidc_token: OidcToken = None,
    ) -> str:
        extra = {}

        if oidc_token:
            if "service_account_email" not in oidc_token:
                oidc_token[
                    "service_account_email"
                ] = self._project.service_account_email

            extra["oidc_token"] = oidc_token

        task_name = task_name or f"task-{ulid.new().str}"
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {"Content-type": "application/json"},
                "body": payload,
            },
            "name": self.get_task_path(queue, task_name),
            **extra,
        }

        # Send the task
        parent = self.get_queue_path(queue)
        response = self._client.create_task(request={"parent": parent, "task": task})

        logger.debug("Created task %s", response.name)

        return response.name


Task = namedtuple("Task", "task_url queue payload task_name")


class InMemoryEnqueuer:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._tasks = []

    @property
    def enqueued_tasks(self) -> list[tuple]:
        return self._tasks

    def enqueue_http_request(
        self,
        url: str,
        queue: str,
        payload: bytes,
        task_name: str = None,
        oidc_token: OidcToken = None,
    ) -> str:
        task_name = task_name or f"memory-task-{ulid.new().str}"
        self._tasks.append(Task(url, queue, payload, task_name))

        return f"projects/fake/locations/us-central1/queues/{queue}/tasks/{task_name}"
