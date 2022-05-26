import os
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional, Union

import pytz
from apscheduler.schedulers.base import BaseScheduler

from dropland.log import logger, tr
from dropland.storages.redis import USE_REDIS
from dropland.storages.sql import SqlStorageEngine


@dataclass
class EngineConfig:
    sql_url: Union[str, SqlStorageEngine] = None
    sql_tablename: Optional[str] = None
    redis_url: Optional[str] = None
    redis_job_key: Optional[str] = None

    job_coalesce: bool = False
    job_max_instances: int = 1
    job_misfire_grace_time: int = 24 * 3600

    task_host: str = '0.0.0.0'
    task_port: int = 3000
    task_processes: int = os.cpu_count()
    task_workers: int = os.cpu_count()
    task_rpc_timeout_seconds: int = 5
    create_remote_engine: Optional[bool] = None
    timezone: str = 'UTC'


class TaskManagerBackend:
    def __init__(self, is_scheduler: bool):
        self._engines: Dict[str, BaseScheduler] = dict()
        self._is_scheduler = is_scheduler

    @property
    def name(self) -> str:
        return 'scheduler'

    def create_engine(self, name: str, config: EngineConfig) -> Optional[BaseScheduler]:
        if engine := self._engines.get(name):
            return engine

        from apscheduler.jobstores.memory import MemoryJobStore

        jobstores = {'default': MemoryJobStore()}

        if USE_REDIS and config.redis_url:
            from apscheduler.jobstores.redis import RedisJobStore
            from redis import ConnectionPool

            jobstores['redis'] = RedisJobStore(
                connection_pool=ConnectionPool.from_url(config.redis_url),
                jobs_key=f'{config.redis_job_key}.aps.jobs'
                    if isinstance(config.redis_job_key, str) else 'apscheduler.jobs',
                run_times_key=f'{config.redis_job_key}.aps.run_times'
                    if isinstance(config.redis_job_key, str) else 'apscheduler.run_times',
            )

        if config.sql_url:
            from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

            jobstores['sql'] = SQLAlchemyJobStore(
                url=config.sql_url if isinstance(config.sql_url, str) else None,
                engine=config.sql_url if not isinstance(config.sql_url, str) else None,
                metadata=config.sql_url.metadata if not isinstance(config.sql_url, str) else None,
                tablename=config.sql_tablename if config.sql_tablename else 'apscheduler_jobs',
                engine_options={'pool_pre_ping': True},
            )

        job_defaults = {
            'coalesce': config.job_coalesce,
            'max_instances': config.job_max_instances,
            'misfire_grace_time': config.job_misfire_grace_time,
        }

        engine = self._create_engine(config, jobstores=jobstores, job_defaults=job_defaults)
        self._engines[name] = engine
        logger.info(tr('dropland.scheduler.created'))
        return engine

    def get_engine(self, name: str) -> Optional[BaseScheduler]:
        return self._engines.get(name)

    def get_engine_names(self) -> List[str]:
        return list(self._engines.keys())

    def _create_engine(self, config: EngineConfig, **kwargs):
        from apscheduler.executors.asyncio import AsyncIOExecutor
        from apscheduler.executors.pool import ProcessPoolExecutor
        from concurrent.futures.thread import ThreadPoolExecutor as BackgroundExecutor
        from dropland.tasks.local import Scheduler

        logger.info(tr('dropland.scheduler.create.local'))

        executors = {
            'default': AsyncIOExecutor(),
            'process': ProcessPoolExecutor(config.task_processes),
        }

        if config.timezone:
            timezone = pytz.timezone(config.timezone) if isinstance(config.timezone, str) else config.timezone
        else:
            timezone = None

        create_remote_engine = config.create_remote_engine and not self._is_scheduler
        executor = BackgroundExecutor(config.task_workers, thread_name_prefix='TaskWorker')
        scheduler = Scheduler(
            remote=self._create_remote(config) if create_remote_engine else None,
            executor=executor, executors=executors, timezone=timezone, **kwargs
        )
        return scheduler

    def _create_remote(self, config: EngineConfig):
        import apscheduler.jobstores.base
        from dropland.tasks.remote import RemoteScheduler, register_exception

        logger.info(tr('dropland.scheduler.create.remote'))

        register_exception(apscheduler.jobstores.base.JobLookupError)
        register_exception(apscheduler.jobstores.base.ConflictingIdError)
        register_exception(apscheduler.jobstores.base.TransientJobError)

        return RemoteScheduler(
            host=config.task_host, port=config.task_port,
            rpc_timeout=timedelta(seconds=config.task_rpc_timeout_seconds)
        )
