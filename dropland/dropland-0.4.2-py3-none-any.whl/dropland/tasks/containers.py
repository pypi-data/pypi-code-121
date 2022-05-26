import os
import sys

from dependency_injector import containers, providers

from dropland.tasks import USE_SCHEDULER
from dropland.util import default_value

if USE_SCHEDULER:
    from dropland.tasks.engine import TaskManagerBackend, EngineConfig


if USE_SCHEDULER:
    import dropland.tasks.service

    class SimpleSchedulerModule(containers.DeclarativeContainer):
        __self__ = providers.Self()

        # noinspection PyMethodMayBeStatic
        def _is_scheduler(self):
            return 'worker' == sys.argv[0]

        is_scheduler = providers.Factory(_is_scheduler, __self__)
        engine_factory = providers.Singleton(TaskManagerBackend, is_scheduler)

        def _create_engine(self, *args, **kwargs):
            return self.engine_factory().create_engine(*args, **kwargs)

        create_engine = providers.Factory(_create_engine, __self__)
        instance = providers.Singleton(create_engine)
        wiring_config = containers.WiringConfiguration(modules=[dropland.tasks.service])


    class SchedulerModule(SimpleSchedulerModule):
        __self__ = providers.Self()
        config = providers.Configuration()

        def _create_engine(self):
            if isinstance(self.config.engine_config(), EngineConfig):
                engine_config = self.config.engine_config()
            else:
                engine_config = EngineConfig(
                    sql_url=self.config.engine_config.sql_url(),
                    sql_tablename=self.config.engine_config.sql_tablename(),
                    redis_url=self.config.engine_config.redis_url(),
                    redis_job_key=self.config.engine_config.redis_job_key(),
                    job_coalesce=self.config.engine_config.job_coalesce.as_(bool)(),
                    job_max_instances=self.config.engine_config.
                        job_max_instances.as_(default_value(int))(default=1),
                    job_misfire_grace_time=self.config.engine_config.
                        job_misfire_grace_time.as_(default_value(int))(default=24 * 3600),
                    task_host=self.config.engine_config.task_host(),
                    task_port=self.config.engine_config.task_port(),
                    task_processes=self.config.engine_config.
                        task_processes.as_(default_value(int))(default=os.cpu_count()),
                    task_workers=self.config.engine_config.
                        task_workers.as_(default_value(int))(default=os.cpu_count()),
                    task_rpc_timeout_seconds=self.config.engine_config.
                        task_rpc_timeout_seconds.as_(default_value(int))(default=5),
                    create_remote_engine=self.config.engine_config.create_remote_engine.as_(bool)(),
                    timezone=self.config.engine_config.timezone(default='UTC')
                )
            return SimpleSchedulerModule._create_engine(self, self.config.name(), engine_config)

        create_engine = providers.Factory(_create_engine, __self__)
        instance = providers.Singleton(create_engine)
        wiring_config = containers.WiringConfiguration(modules=[dropland.tasks.service])
