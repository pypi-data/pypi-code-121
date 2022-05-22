import logging
import os
from typing import Callable, Dict, List, Optional

import attr
from psycopg.errors import DatabaseError
from psycopg.rows import dict_row

from worker_bunch.database.database_config import DatabaseConfKey, MqttOutputType, DATABASE_WORKER_JSONSCHEMA
from worker_bunch.database.database_connector import DatabaseConnector
from worker_bunch.database.database_manager import DatabaseManager
from worker_bunch.database.database_utils import DatabaseUtils
from worker_bunch.dispatcher import Dispatcher
from worker_bunch.notification import Notification, NT
from worker_bunch.service_config import ConfigException
from worker_bunch.utils.time_utils import TimeUtils
from worker_bunch.worker.worker import Worker, WorkerSetup


@attr.define
class Step:
    """Property names from `DatabaseConfKey` must match!"""

    script_file: str = None
    statement: str = None
    replacements: Dict[str, str] = attr.Factory(dict)

    mqtt_last_will: str = None
    mqtt_output_type: str = None
    mqtt_retain: bool = False
    mqtt_topic: str = None


class DatabaseWorker(Worker):

    CRON_TOPIC = "cron"

    def __init__(self, name: str):
        super().__init__(name)

        self._database_manager: Optional[DatabaseManager] = None
        self._connection_key: Optional[str] = None
        self._cron: Optional[str] = None
        self._steps: List[Step] = []
        self._replacements: Dict[str, str] = {}

    def setup(self, props):
        super().setup(props)

        self._database_manager = props[WorkerSetup.DATABASE_MANAGER]

        self._connection_key = self._worker_settings[DatabaseConfKey.CONNECTION_KEY]
        self._cron = self._worker_settings[DatabaseConfKey.CRON]
        self._replacements = self._worker_settings.get(DatabaseConfKey.REPLACEMENTS, {})

        self._steps = []
        config_steps = self._worker_settings[DatabaseConfKey.STEPS]

        found_config_error = False

        def push_error(message: str):
            nonlocal found_config_error
            self._logger.error("config issue - step" + message)
            found_config_error = True

        for index, config_step in enumerate(config_steps):
            step = self.create_step(config_step)
            self._steps.append(step)
            self.prepare_step(step, index, push_error)

        if found_config_error:
            raise ConfigException("Some configuration issues occurred! See log.")

    def get_partial_settings_schema(self) -> Optional[Dict[str, any]]:
        return DATABASE_WORKER_JSONSCHEMA

    def make_partial_settings_required(self) -> bool:
        return True

    def set_last_will(self):
        for step in self._steps:
            if step.mqtt_topic and step.mqtt_last_will:
                self._mqtt_proxy.set_last_will(step.mqtt_topic, step.mqtt_last_will, step.mqtt_retain)

    def subscribe_notifications(self, dispatcher: Dispatcher):
        dispatcher.subscribe_cron(self, self._cron, self.CRON_TOPIC)

    def _work(self, notifications: List[Notification]):
        if not Notification.find(notifications, NT.CRON) and not Notification.find(notifications, NT.SINGLE_STARTED):
            return

        times_log = ""
        time_sum = 0

        database = self._database_manager.create(self.name, self._connection_key)
        with database:
            for index, step in enumerate(self._steps):
                self.proceed()  # raises ShutdownException

                time_start = TimeUtils.now()
                try:
                    if step.mqtt_output_type == MqttOutputType.JSON:
                        self._query_json(database, step)
                    elif step.mqtt_output_type == MqttOutputType.SCALAR:
                        self._query_scalar(database, step)
                    else:
                        self._execute(database, step)

                    database.connection.commit()

                except DatabaseError as ex:
                    self._logger.error(ex)
                    database.connection.rollback()

                time_diff = TimeUtils.diff_seconds(time_start)
                time_sum += time_diff
                if self._logger.isEnabledFor(logging.DEBUG):
                    output_type = f" ({step.mqtt_output_type})" if step.mqtt_output_type else ""
                    self._logger.debug("[%d]: executed statement%s:\n%s", index, output_type, step.statement)
                if time_diff > 0.2 and 1 < len(self._steps):
                    times_log += f"[{index}]={time_diff:.1f}s; "

            times_log += f"sum={time_sum:.1f}s"
            self._logger.info("took: %s", times_log)

    def _final_work(self):
        for step in self._steps:
            if step.mqtt_topic and step.mqtt_last_will:
                self._mqtt_proxy.queue(step.mqtt_topic, step.mqtt_last_will, step.mqtt_retain)

    def _query_json(self, database: DatabaseConnector, step: Step):
        with database.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(step.statement)
            fetched = cursor.fetchone()

            self._mqtt_proxy.queue(step.mqtt_topic, fetched, step.mqtt_retain)

    def _query_scalar(self, database: DatabaseConnector, step: Step):
        with database.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(step.statement)
            fetched = cursor.fetchone()

            if len(fetched) != 1:
                raise ConfigException("Scalar statement must return exactly 1 result column!")

            payload = str(list(fetched.values())[0])
            self._mqtt_proxy.queue(step.mqtt_topic, payload, step.mqtt_retain)

    @classmethod
    def _execute(cls, database: DatabaseConnector, step: Step):
        with database.connection.cursor() as cursor:
            cursor.execute(step.statement)

    @classmethod
    def create_step(cls, config_step: Dict[str, any]) -> Step:
        return Step(**config_step)

    def prepare_step(self, step: Step, index: int, push_error: Callable):
        if step.mqtt_output_type == MqttOutputType.NONE or not step.mqtt_output_type:
            step.mqtt_output_type = None
        step.mqtt_retain = bool(step.mqtt_retain)

        if not step.mqtt_topic and (step.mqtt_last_will or step.mqtt_output_type):
            push_error(f"[{index}]: missing mqtt topic!")

        self.prepare_step_statement(step, index, push_error)

    def prepare_step_statement(self, step: Step, index: int, push_error: Callable):
        if not step.statement:  # must be from file
            if not os.path.isfile(step.script_file):
                push_error(f"[{index}]: script file ({step.script_file}) not found!")
                return

            try:
                step.statement = DatabaseUtils.load_script_file(step.script_file)
            except IOError as ex:
                push_error(f"[{index}]: script file ({step.script_file}) cannot be read! {str(ex)}")

        replacements = {**self._replacements, **step.replacements}
        for pattern, replacement in replacements.items():
            step.statement = step.statement.replace(pattern, replacement)

        step.statement = step.statement.strip()
        if not step.statement:
            push_error(f"[{index}]: script file ({step.script_file}) is empty!")
            return
