import os

from pydantic import BaseSettings


class SchedulerSettings(BaseSettings):
    TASK_HOST: str = '0.0.0.0'
    TASK_PORT: int = 3000
    TASK_PROCESSES: int = os.cpu_count()
    TASK_WORKERS: int = os.cpu_count()
    TASK_RPC_TIMEOUT_SECONDS: int = 5
    TASK_CREATE_REMOTE: bool = False

    class Config:
        case_sensitive = False
        env_file = '.env'
