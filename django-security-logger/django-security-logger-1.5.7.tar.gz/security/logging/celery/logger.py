from django.utils.timezone import now

from security.enums import LoggerName
from security.logging.common import SecurityLogger
from security.backends.signals import (
    celery_task_invocation_started, celery_task_invocation_triggered, celery_task_invocation_ignored,
    celery_task_invocation_timeout, celery_task_invocation_expired, celery_task_run_started, celery_task_run_succeeded,
    celery_task_run_failed, celery_task_run_retried, celery_task_run_output_updated, celery_task_invocation_succeeded,
    celery_task_invocation_failed, celery_task_invocation_duplicate
)


class CeleryInvocationLogger(SecurityLogger):

    logger_name = LoggerName.CELERY_TASK_INVOCATION
    store = False

    def __init__(self, name=None, queue_name=None, input=None, task_args=None, task_kwargs=None, applied_at=None,
                 is_async=None, is_unique=None, is_on_commit=None, triggered_at=None, stale_at=None,
                 estimated_time_of_first_arrival=None, expires_at=None, celery_task_id=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.input = input
        self.queue_name = queue_name
        self.task_args = task_args
        self.task_kwargs = task_kwargs
        self.applied_at = applied_at
        self.is_async = is_async
        self.is_unique = is_unique
        self.is_on_commit = is_on_commit
        self.triggered_at = triggered_at
        self.stale_at = stale_at
        self.estimated_time_of_first_arrival = estimated_time_of_first_arrival
        self.expires_at = expires_at
        self.celery_task_id = celery_task_id

    def log_started(self, name, queue_name, task_args, task_kwargs, applied_at,
                    is_async, is_unique, is_on_commit):
        task_input = []
        if task_args:
            task_input += [str(v) for v in task_args]
        if task_kwargs:
            task_input += ['{}={}'.format(k, v) for k, v in task_kwargs.items()]
        self.name = name
        self.queue_name = queue_name
        self.input = ', '.join(task_input)
        self.task_args = list(task_args)
        self.task_kwargs = task_kwargs
        self.applied_at = applied_at
        self.is_async = is_async
        self.is_unique = is_unique
        self.is_on_commit = is_on_commit
        self.start = now()
        celery_task_invocation_started.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_triggered(self, triggered_at, stale_at, estimated_time_of_first_arrival,
                      expires_at, celery_task_id):
        self.triggered_at = triggered_at
        self.stale_at = stale_at
        self.estimated_time_of_first_arrival = estimated_time_of_first_arrival
        self.expires_at = expires_at
        self.celery_task_id = celery_task_id
        celery_task_invocation_triggered.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_unique(self, triggered_at, stale_at, estimated_time_of_first_arrival,
                   expires_at, celery_task_id):
        self.triggered_at = triggered_at
        self.stale_at = stale_at
        self.estimated_time_of_first_arrival = estimated_time_of_first_arrival
        self.expires_at = expires_at
        self.celery_task_id = celery_task_id
        celery_task_invocation_duplicate.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_ignored(self):
        self.stop = now()
        celery_task_invocation_ignored.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_timeout(self):
        self.stop = now()
        celery_task_invocation_timeout.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_expired(self):
        self.stop = now()
        celery_task_invocation_expired.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_succeeded(self):
        self.stop = now()
        celery_task_invocation_succeeded.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_failed(self):
        self.stop = now()
        celery_task_invocation_failed.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )


class CeleryTaskRunLogger(SecurityLogger):

    logger_name = LoggerName.CELERY_TASK_RUN

    def __init__(self, name=None, queue_name=None, input=None, task_args=None, task_kwargs=None, retries=None,
                 waiting_time=None, celery_task_id=None, result=None, output=None, estimated_time_of_next_retry=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.input = input
        self.queue_name = queue_name
        self.task_args = task_args
        self.task_kwargs = task_kwargs
        self.retries = retries
        self.waiting_time = waiting_time
        self.celery_task_id = celery_task_id
        self.result = result
        self.output = output
        self.estimated_time_of_next_retry = estimated_time_of_next_retry

    def log_started(self, name, queue_name, task_args, task_kwargs, celery_task_id, retries, trigger_time):
        task_input = []
        if task_args:
            task_input += [str(v) for v in task_args]
        if task_kwargs:
            task_input += ['{}={}'.format(k, v) for k, v in task_kwargs.items()]
        self.start = now()
        self.name = name
        self.celery_task_id = celery_task_id
        self.queue_name = queue_name
        self.input = ', '.join(task_input)
        self.task_args = list(task_args)
        self.task_kwargs = task_kwargs
        self.retries = retries
        self.waiting_time = (self.start - trigger_time).total_seconds()
        celery_task_run_started.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_succeeded(self, result):
        self.result = result
        self.stop = now()
        celery_task_run_succeeded.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_failed(self, ex_tb):
        self.error_message = ex_tb
        self.stop = now()
        celery_task_run_failed.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_retried(self, ex_tb, estimated_time_of_next_retry):
        self.error_message = ex_tb
        self.stop = now()
        self.estimated_time_of_next_retry = estimated_time_of_next_retry
        celery_task_run_retried.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_output_updated(self, output):
        self.output = output
        celery_task_run_output_updated.send(sender=CeleryTaskRunLogger, logger=self)
