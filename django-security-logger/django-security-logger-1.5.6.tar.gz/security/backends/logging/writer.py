import logging

from security.backends.writer import BaseBackendWriter


input_request_logger = logging.getLogger('security.input_request')
output_request_logger = logging.getLogger('security.output_request')
command_logger = logging.getLogger('security.command')
celery_logger = logging.getLogger('security.celery')


class LoggingBackendWriter(BaseBackendWriter):

    def input_request_started(self, logger):
        input_request_logger.info(
            'Input request "%(id)s" to "%(host)s" with path "%(path)s" was started',
            dict(
                id=logger.id,
                host=logger.host,
                path=logger.path,
            ),
            extra=dict(
                id=logger.id,
                input_request_host=logger.host,
                input_request_path=logger.path,
                input_request_method=logger.method,
                input_request_view_slug=logger.view_slug,
                input_request_slug=logger.slug,
                input_request_is_secure=logger.is_secure,
                input_request_ip=logger.ip,
                input_request_release=logger.release
            )
        )

    def input_request_finished(self, logger):
        input_request_logger.info(
            'Input request "%(id)s" to "%(host)s" with path "%(path)s" was finished',
            dict(
                id=logger.id,
                host=logger.host,
                path=logger.path,
            ),
            extra=dict(
                id=logger.id,
                input_request_host=logger.host,
                input_request_path=logger.path,
                input_request_method=logger.method,
                input_request_view_slug=logger.view_slug,
                input_request_slug=logger.slug,
                input_request_is_secure=logger.is_secure,
                input_request_ip=logger.ip,
                input_request_response_code=logger.response_code,
                input_request_start=logger.start,
                input_request_stop=logger.stop,
                input_request_time=logger.time,
                input_request_release=logger.release
            )
        )

    def input_request_error(self, logger):
        input_request_logger.error(
            'Input request "%(id)s" to "%(host)s" with path "%(path)s" failed',
            dict(
                id=logger.id,
                host=logger.host,
                path=logger.path,
            ),
            extra=dict(
                id=logger.id,
                input_request_host=logger.host,
                input_request_path=logger.path,
                input_request_method=logger.method,
                input_request_view_slug=logger.view_slug,
                input_request_slug=logger.slug,
                input_request_is_secure=logger.is_secure,
                input_request_ip=logger.ip,
                input_request_start=logger.start,
                input_request_release=logger.release
            )
        )

    def output_request_started(self, logger):
        output_request_logger.info(
            'Output request "%(id)s" to "%(host)s" with path "%(path)s" was started',
            dict(
                id=logger.id,
                host=logger.host,
                path=logger.path,
            ),
            extra=dict(
                id=logger.id,
                output_request_host=logger.host,
                output_request_path=logger.path,
                output_request_method=logger.method,
                output_request_slug=logger.slug,
                output_request_is_secure=logger.is_secure,
                output_request_release=logger.release
            )
        )

    def output_request_finished(self, logger):
        output_request_logger.info(
            'Output request "%(id)s" to "%(host)s" with path "%(path)s" was successful',
            dict(
                id=logger.id,
                host=logger.host,
                path=logger.path,
            ),
            extra=dict(
                id=logger.id,
                output_request_host=logger.host,
                output_request_path=logger.path,
                output_request_method=logger.method,
                output_request_slug=logger.slug,
                output_request_is_secure=logger.is_secure,
                output_request_response_code=logger.response_code,
                output_request_start=logger.start,
                output_request_stop=logger.stop,
                output_request_time=logger.time,
                output_request_release=logger.release
            )
        )

    def output_request_error(self, logger):
        output_request_logger.error(
            'Output request "%(id)s" to "%(host)s" with path "%(path)s" failed',
            dict(
                id=logger.id,
                host=logger.host,
                path=logger.path,
            ),
            extra=dict(
                id=logger.id,
                output_request_host=logger.host,
                output_request_path=logger.path,
                output_request_method=logger.method,
                output_request_slug=logger.slug,
                output_request_is_secure=logger.is_secure,
                output_request_start=logger.start,
                output_request_stop=logger.stop,
                output_request_time=logger.time,
                output_request_release=logger.release
            )
        )

    def command_started(self, logger):
        command_logger.info(
            'Command "%(id)s" with name "%(name)s" was started',
            dict(
                id=logger.id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                command_name=logger.name,
                command_is_executed_from_command_line=logger.is_executed_from_command_line,
                command_start=logger.start,
                command_release=logger.release
            )
        )

    def command_output_updated(self, logger):
        """Output is not stored into log"""

    def command_finished(self, logger):
        command_logger.info(
            'Command "%(id)s" with name "%(name)s" was successful',
            dict(
                id=logger.id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                command_name=logger.name,
                command_is_executed_from_command_line=logger.is_executed_from_command_line,
                command_start=logger.start,
                command_stop=logger.stop,
                command_time=logger.time,
                command_is_error=False,
                command_release=logger.release
            )
        )

    def command_error(self, logger):
        command_logger.error(
            'Command "%(id)s" with name "%(name)s" failed',
            dict(
                id=logger.id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                command_name=logger.name,
                command_is_executed_from_command_line=logger.is_executed_from_command_line,
                command_start=logger.start,
                command_stop=logger.stop,
                command_time=logger.time,
                command_is_error=True,
                command_release=logger.release
            )
        )

    def celery_task_invocation_started(self, logger):
        """Invocation started means nothing for logging backend"""

    def celery_task_invocation_duplicate(self, logger):
        celery_logger.info(
            'Celery task invocation "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" is duplicate',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_task_id=logger.celery_task_id,
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_state='DUPLICATE',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_invocation_triggered(self, logger):
        celery_logger.info(
            'Celery task invocation "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was invoked',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_task_id=logger.celery_task_id,
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_state='TRIGGERED',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_invocation_ignored(self, logger):
        celery_logger.info(
            'Celery task invocation "%(id)s" with name "%(name)s" was ignored',
            dict(
                id=logger.id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_stop=logger.stop,
                celery_task_invocation_time=logger.time,
                celery_task_invocation_state='IGNORED',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_invocation_timeout(self, logger):
        celery_logger.warning(
            'Celery task "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" caused a response timeout',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_task_id=logger.celery_task_id,
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_stop=logger.stop,
                celery_task_invocation_time=logger.time,
                celery_task_invocation_state='TIMEOUT',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_invocation_succeeded(self, logger):
        celery_logger.info(
            'Celery task invocation "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was successful',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id or '',
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_task_id=logger.celery_task_id or '',
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_stop=logger.stop,
                celery_task_invocation_time=logger.time,
                celery_task_invocation_state='SUCCEEDED',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_invocation_failed(self, logger):
        celery_logger.info(
            'Celery task invocation "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was failed',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id or '',
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_task_id=logger.celery_task_id or '',
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_stop=logger.stop,
                celery_task_invocation_time=logger.time,
                celery_task_invocation_state='FAILED',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_invocation_expired(self, logger):
        celery_logger.error(
            'Celery task invocation "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was expired',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id or '',
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_invocation_task_id=logger.celery_task_id or '',
                celery_task_invocation_name=logger.name,
                celery_task_invocation_queue=logger.queue_name,
                celery_task_invocation_start=logger.start,
                celery_task_invocation_stop=logger.stop,
                celery_task_invocation_time=logger.time,
                celery_task_invocation_state='EXPIRED',
                celery_task_invocation_release=logger.release
            ),
        )

    def celery_task_run_started(self, logger):
        celery_logger.info(
            'Celery task "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was started',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_name=logger.name,
                celery_task_queue=logger.queue_name,
                celery_task_start=logger.start,
                celery_task_invocation_state='ACTIVE',
                celery_task_attempt=logger.retries,
                celery_task_release=logger.release,
                celery_task_waiting_time=logger.waiting_time
            ),
        )

    def celery_task_run_succeeded(self, logger):
        celery_logger.info(
            'Celery task "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was successful',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_name=logger.name,
                celery_task_queue=logger.queue_name,
                celery_task_start=logger.start,
                celery_task_invocation_state='SUCCEEDED',
                celery_task_attempt=logger.retries,
                celery_task_stop=logger.stop,
                celery_task_time=logger.time,
                celery_task_release=logger.release,
                celery_task_waiting_time=logger.waiting_time
            )
        )

    def celery_task_run_failed(self, logger):
        celery_logger.error(
            'Celery task "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" failed',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_name=logger.name,
                celery_task_queue=logger.queue_name,
                celery_task_start=logger.start,
                celery_task_invocation_state='FAILED',
                celery_task_attempt=logger.retries,
                celery_task_stop=logger.stop,
                celery_task_time=logger.time,
                celery_task_release=logger.release,
                celery_task_waiting_time=logger.waiting_time
            )
        )

    def celery_task_run_retried(self, logger):
        celery_logger.warning(
            'Celery task "%(id)s" with celery id "%(celery_task_id)s" and name "%(name)s" was repeated',
            dict(
                id=logger.id,
                celery_task_id=logger.celery_task_id,
                name=logger.name,
            ),
            extra=dict(
                id=logger.id,
                celery_task_name=logger.name,
                celery_task_queue=logger.queue_name,
                celery_task_start=logger.start,
                celery_task_invocation_state='RETRIED',
                celery_task_attempt=logger.retries,
                celery_task_stop=logger.stop,
                celery_task_time=logger.time,
                celery_task_release=logger.release,
                celery_task_waiting_time=logger.waiting_time
            )
        )

    def celery_task_run_output_updated(self, logger):
        """Output is not stored into log"""
