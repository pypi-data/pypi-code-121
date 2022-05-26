from fastapi import FastAPI

from dropland.log import logger, tr
from dropland.tasks import USE_SCHEDULER, Scheduler


def add_scheduler(app: FastAPI, scheduler: Scheduler):
    if not USE_SCHEDULER:
        return

    @app.on_event('startup')
    def init_task():
        app.state.scheduler = scheduler
        if not scheduler.running:
            scheduler.start()

        logger.info(tr('dropland.scheduler.started'))

    @app.on_event('shutdown')
    def fini_task():
        scheduler.shutdown(wait=True)
        app.state.scheduler = None

        logger.info(tr('dropland.scheduler.stopped'))
