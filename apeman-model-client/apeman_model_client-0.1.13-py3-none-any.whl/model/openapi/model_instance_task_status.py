from enum import Enum


class TaskStatus(Enum):
    NONE = 'TASK_NONE'
    RUNNING = 'TASK_RUNNING'
    FAILED = 'TASK_FAILED'
    SUCCEEDED = 'TASK_SUCCEEDED'
    CANCELED = 'TASK_CANCELED'
