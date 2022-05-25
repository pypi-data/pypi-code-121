try:
    from apscheduler.schedulers.base import BaseScheduler

    from dropland.tasks.engine import EngineConfig, TaskManagerBackend
    from dropland.tasks.local import Scheduler
    from dropland.tasks.settings import SchedulerSettings

    USE_SCHEDULER = True

except ImportError:
    USE_SCHEDULER = False
