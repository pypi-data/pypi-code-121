import os
import json
import gzip
import math

from io import TextIOWrapper

from datetime import datetime, time

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db import router, transaction
from django.utils.timezone import utc
from django.utils.timezone import now
from django.utils.module_loading import import_string

from celery import current_app
from celery.exceptions import NotRegistered

from chamber.shortcuts import change_and_save

from security.backends.writer import BaseBackendWriter
from security.config import settings
from security.enums import RequestLogState, CeleryTaskInvocationLogState, CeleryTaskRunLogState, CommandState

from .models import CeleryTaskInvocationLog, get_log_model_from_logger_name, get_response_state


MAX_VERSION = 9999


def lazy_serialize_qs_without_pk(qs):
    def generator():
        for obj in qs.iterator():
            data = serializers.serialize('python', [obj])[0]
            yield data

    class StreamList(list):
        def __iter__(self):
            return generator()

        def __len__(self):
            return 1

    return StreamList()


def get_querysets_by_batch(qs, batch):
    steps = math.ceil(qs.count() / batch)
    for _ in range(steps):
        yield qs[:batch]


class SQLBackendWriter(BaseBackendWriter):

    def _set_related_objects(self, log, logger):
        log.related_objects.add(
            *[related_object_triple[1:] for related_object_triple in logger.related_objects]
        )

    def _get_version(self, logger, is_last):
        if is_last:
            return MAX_VERSION
        elif 'last_sql_version' in logger.backend_logs:
            return logger.backend_logs.last_sql_version + 1
        else:
            return 0

    def _create_from_logger(self, logger, is_last, **extra_data):
        version = self._get_version(logger, is_last)
        data = logger.to_dict()
        del data['related_objects']

        model_class = get_log_model_from_logger_name(logger.logger_name)
        if not model_class.objects.filter(id=logger.id, version__gte=version).exists():
            instance = model_class(
                version=version,
                **extra_data,
                **data
            )
            instance.save()
            self._set_related_objects(instance, logger)
            logger.backend_logs.sql_instance = instance
            logger.backend_logs.last_sql_version = version

    def _update_from_logger(self, logger, is_last, **extra_data):
        version = self._get_version(logger, is_last)
        data = logger.to_dict()
        del data['related_objects']

        with transaction.atomic(using=settings.LOG_DB_NAME):
            instance = logger.backend_logs.sql_instance.__class__.objects.select_for_update().get(id=logger.id)
            if instance.version < version:
                instance = change_and_save(
                    logger.backend_logs.sql_instance,
                    version=version,
                    **data,
                    **extra_data,
                    update_only_changed_fields=True,
                )
                self._set_related_objects(instance, logger)
            logger.backend_logs.sql_instance = instance
            logger.backend_logs.last_sql_version = version

    def _create_or_update_from_logger(self, logger, is_last=False, **extra_data):
        if 'sql_instance' in logger.backend_logs:
            self._update_from_logger(logger, is_last, **extra_data)
        else:
            self._create_from_logger(logger, is_last, **extra_data)

    def input_request_started(self, logger):
        self._create_or_update_from_logger(logger, state=RequestLogState.INCOMPLETE)

    def input_request_finished(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=get_response_state(logger.response_code)
        )

    def input_request_error(self, logger):
        self._create_or_update_from_logger(logger, state=RequestLogState.ERROR)

    def output_request_started(self, logger):
        self._create_or_update_from_logger(logger, state=RequestLogState.INCOMPLETE)

    def output_request_finished(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=get_response_state(logger.response_code)
        )

    def output_request_error(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=RequestLogState.ERROR
        )

    def command_started(self, logger):
        self._create_or_update_from_logger(
            logger, state=CommandState.ACTIVE
        )

    def command_output_updated(self, logger):
        self._create_or_update_from_logger(
            logger, state=CommandState.ACTIVE
        )

    def command_finished(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CommandState.SUCCEEDED
        )

    def command_error(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CommandState.FAILED
        )

    def celery_task_invocation_started(self, logger):
        self._create_or_update_from_logger(
            logger, state=CeleryTaskInvocationLogState.WAITING
        )

    def celery_task_invocation_triggered(self, logger):
        self._create_or_update_from_logger(
            logger, state=CeleryTaskInvocationLogState.TRIGGERED
        )

    def celery_task_invocation_duplicate(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskInvocationLogState.DUPLICATE
        )

    def celery_task_invocation_ignored(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskInvocationLogState.IGNORED
        )

    def celery_task_invocation_timeout(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskInvocationLogState.TIMEOUT
        )

    def celery_task_invocation_expired(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskInvocationLogState.EXPIRED
        )

    def celery_task_invocation_succeeded(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskInvocationLogState.SUCCEEDED
        )

    def celery_task_invocation_failed(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskInvocationLogState.FAILED
        )

    def celery_task_run_started(self, logger):
        self._create_or_update_from_logger(
            logger, state=CeleryTaskRunLogState.ACTIVE
        )

    def celery_task_run_succeeded(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskRunLogState.SUCCEEDED
        )

    def celery_task_run_failed(self, logger):
        self._create_or_update_from_logger(
            logger, is_last=True, state=CeleryTaskRunLogState.FAILED
        )

    def celery_task_run_retried(self, logger):
        self._create_or_update_from_logger(
            logger, state=CeleryTaskRunLogState.RETRIED
        )

    def celery_task_run_output_updated(self, logger):
        self._create_or_update_from_logger(
            logger, state=CeleryTaskRunLogState.ACTIVE
        )

    def set_stale_celery_task_log_state(self):
        processsing_stale_tasks = CeleryTaskInvocationLog.objects.filter_processing(
            stale_at__lt=now()
        ).order_by('stale_at')
        for task in processsing_stale_tasks[:settings.SET_STALE_CELERY_INVOCATIONS_LIMIT_PER_RUN]:
            task_last_run = task.last_run
            if task_last_run and task_last_run.state == CeleryTaskRunLogState.SUCCEEDED:
                change_and_save(
                    task,
                    state=CeleryTaskInvocationLogState.SUCCEEDED,
                    stop=task_last_run.stop,
                    time=(task_last_run.stop - task.start).total_seconds(),
                    version=MAX_VERSION,
                    update_only_changed_fields=True,
                )
            elif task_last_run and task_last_run.state == CeleryTaskRunLogState.FAILED:
                change_and_save(
                    task,
                    state=CeleryTaskInvocationLogState.FAILED,
                    stop=task_last_run.stop,
                    time=(task_last_run.stop - task.start).total_seconds(),
                    version=MAX_VERSION,
                    update_only_changed_fields=True
                )
            else:
                try:
                    current_app.tasks[task.name].expire_invocation(
                        task.id,
                        task.task_args,
                        task.task_kwargs,
                        dict(
                            slug=task.slug,
                            parent_log=task.parent_log,
                            related_objects=[
                                (
                                    router.db_for_write(related_object.object_ct.model_class()),
                                    related_object.object_ct_id,
                                    related_object.object_id
                                ) for related_object in task.related_objects.all()
                            ],
                            start=task.start,
                            celery_task_id=task.celery_task_id,
                            stop=task.stop,
                            name=task.name,
                            queue_name=task.queue_name,
                            applied_at=task.applied_at,
                            triggered_at=task.triggered_at,
                            is_unique=task.is_unique,
                            is_async=task.is_async,
                            is_on_commit=task.is_on_commit,
                            input=task.input,
                            task_args=task.task_args,
                            task_kwargs=task.task_kwargs,
                            estimated_time_of_first_arrival=task.estimated_time_of_first_arrival,
                            expires_at=task.expires_at,
                            stale_at=task.stale_at,
                        )
                    )
                except NotRegistered:
                    change_and_save(
                        task,
                        state=CeleryTaskInvocationLogState.EXPIRED,
                        stop=now(),
                        version=MAX_VERSION,
                        update_only_changed_fields=True
                    )

    def clean_logs(self, type, timestamp, backup_path, stdout):
        storage = import_string(settings.BACKUP_STORAGE_CLASS)()

        qs = get_log_model_from_logger_name(type).objects.filter(stop__lte=timestamp).order_by('stop')
        for step_timestamp in qs.datetimes('start', 'day', tzinfo=utc):
            min_timestamp = datetime.combine(step_timestamp, time.min).replace(tzinfo=utc)
            max_timestamp = datetime.combine(step_timestamp, time.max).replace(tzinfo=utc)
            qs_filtered_by_day = qs.filter(stop__range=(min_timestamp, max_timestamp))

            for qs_batch in get_querysets_by_batch(qs_filtered_by_day, settings.PURGE_LOG_BACKUP_BATCH):
                stdout.write(
                    2 * ' ' + 'Cleaning logs for date {} ({})'.format(
                        step_timestamp.date(), qs_batch.count()
                    )
                )
                if backup_path:
                    log_file_name = os.path.join(backup_path, str(step_timestamp.date()))

                    if storage.exists('{}.json.gz'.format(log_file_name)):
                        i = 1
                        while storage.exists('{}({}).json.gz'.format(log_file_name, i)):
                            i += 1
                        log_file_name = '{}({})'.format(log_file_name, i)

                    stdout.write(4 * ' ' + 'generating backup file: {}.json.gz'.format(log_file_name))

                    with storage.open('{}.json.gz'.format(log_file_name), 'wb') as f:
                        with TextIOWrapper(gzip.GzipFile(filename='{}.json'.format(log_file_name),
                                                         fileobj=f, mode='wb')) as gzf:
                            json.dump(
                                lazy_serialize_qs_without_pk(qs_batch), gzf, cls=DjangoJSONEncoder, indent=5
                            )

                stdout.write(4 * ' ' + 'deleting logs')
                for qs_batch_to_delete in get_querysets_by_batch(qs_batch, settings.PURGE_LOG_DELETE_BATCH):
                    qs_filtered_by_day.filter(pk__in=qs_batch_to_delete).delete()
