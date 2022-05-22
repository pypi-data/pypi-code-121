import json
import logging
import sys
from typing import List, Optional

import click
from jsonschema import ValidationError
from yaml.parser import ParserError

from worker_bunch.astral_times.astral_times_manager import AstralTimesManager
from worker_bunch.service_config import ConfigException
from worker_bunch.service_configurator import ServiceConfigurator
from worker_bunch.service_logging import LOGGING_CHOICES, ServiceLogging
from worker_bunch.database.database_manager import DatabaseManager
from worker_bunch.dispatcher import Dispatcher
from worker_bunch.mqtt.mqtt_client import MqttClient, MqttClientFactory
from worker_bunch.mqtt.mqtt_proxy import MqttProxy
from worker_bunch.runner import Runner
from worker_bunch.utils.time_utils import TimeUtils
from worker_bunch.worker.worker import Worker, WorkerSetup
from worker_bunch.worker.worker_factory import WorkerFactory

_logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--config-file",
    help="Config file",
)
@click.option(
    "--json-schema",
    is_flag=True,
    help="Prints the config file JSON schema and exits. (JSON schema is used to validate the YAML config.)"
)
@click.option(
    "--log-file",
    help="Log file (if stated journal logging is disabled)"
)
@click.option(
    "--log-level",
    help="Log level",
    type=click.Choice(LOGGING_CHOICES, case_sensitive=False),
)
@click.option(
    "--print-log-console",
    is_flag=True,
    help="Print log output to console too."
)
@click.option(
    "--skip-log-times",
    is_flag=True,
    help="Skip log timestamp (systemd/journald logs get their own timestamp)."
)
@click.option(
    "--test-single",
    help="Test/debug/run a single worker, once, single-threaded...",
)
def worker_bunch_main(config_file, json_schema, log_file, log_level, print_log_console, skip_log_times, test_single):
    """A task/rule engine framework. It bunches a set of worker threads."""
    # noinspection SpellCheckingInspection
    config_error_code = 78  # sysexits.h: define EX_CONFIG 78 /* configuration error */

    try:
        if json_schema:
            output = generate_json_schema_info(config_file)
            print(output)
        else:
            run_service(config_file, log_file, log_level, print_log_console, skip_log_times, test_single)

    except KeyboardInterrupt:
        pass  # exits 0 by default
    except ConfigException as ex:
        _logger.error(ex)
        sys.exit(config_error_code)

    except ParserError as ex:
        _logger.error("parsing error in config file:\n%s", ex)
        sys.exit(config_error_code)
    except ValidationError as ex:
        _logger.error("error in config file (see JSON schema):\n"
                      "    json-path: %s\n"
                      "    problem:   %s\n"
                      "    validator: %s (argument(s): %s)",
                      ex.json_path, ex.message, ex.validator, ex.validator_value)
        sys.exit(config_error_code)
    except Exception as ex:
        _logger.exception(ex)
        sys.exit(1)  # a simple return is not understood by click


def _shutdown_workers(workers: List[Worker]):
    for worker in workers:
        try:
            worker.stop()
        except Exception as ex:
            _logger.exception(ex)

    time_to_wait = 10.0

    while True:
        time_to_wait -= TimeUtils.sleep(0.02)
        alive_workers = [w for w in workers if w.is_alive()]
        if not alive_workers:
            break
        if time_to_wait < 0:
            _logger.warn("workers doesn't closing properly: %s", ",".join([w.name for w in workers]))
            break


def run_service(config_file, log_file, log_level, print_log_console, skip_log_times, test_single):
    dispatcher: Optional[Dispatcher] = None
    mqtt_client: Optional[MqttClient] = None
    mqtt_proxy: Optional[MqttProxy] = None
    workers: List[Worker] = []

    try:
        # configuring
        service_config = ServiceConfigurator()
        service_config.read_config_file(config_file)

        ServiceLogging.configure(
            service_config.get_logging_config(),
            log_file, log_level, print_log_console, skip_log_times
        )
        _logger.debug("start")

        service_config.init_locale()
        service_config.init_data_dir()

        worker_instances_config = service_config.get_worker_instances_config()
        worker_dict = WorkerFactory.create_workers(worker_instances_config)
        workers_settings_declarations = WorkerFactory.extract_workers_settings_declarations(worker_dict)

        service_config.revalidate_worker_settings(workers_settings_declarations)

        if test_single:
            single_worker = worker_dict.get(test_single)
            if not single_worker:
                raise ConfigException(f"single-run ({test_single}) does not exist!")
            worker_dict = {test_single: single_worker}

        workers = list(worker_dict.values())

        # bootstrapping
        astral_time_manager = AstralTimesManager(service_config.get_astral_config())
        dispatcher = Dispatcher(astral_time_manager)
        database_manager = DatabaseManager(service_config.get_database_config())

        mqtt_config = service_config.get_mqtt_config()
        mqtt_client = MqttClientFactory.create(mqtt_config) if mqtt_config else None
        mqtt_proxy = MqttProxy(mqtt_client)

        workers_settings = service_config.get_worker_settings()

        data_dir = service_config.get_data_dir()
        for worker in workers:
            worker.setup({
                WorkerSetup.ASTRAL_TIME_MANAGER: astral_time_manager,
                WorkerSetup.BASE_DATA_DIR: data_dir,
                WorkerSetup.DATABASE_MANAGER: database_manager,
                WorkerSetup.MQTT_PROXY: mqtt_proxy,
                WorkerSetup.WORKER_SETTINGS: workers_settings.get(worker.name),
            })
            worker.set_last_will()  # before set_mqtt_proxy ("last will" depends on config)!

        # start
        runner = Runner(dispatcher, mqtt_proxy, workers)
        if test_single:
            runner.run_single()
        else:
            runner.run()

    finally:
        _logger.info("shutdown")

        if dispatcher is not None:  # first: stop
            try:
                dispatcher.close()
            except Exception as ex:
                _logger.exception(ex)

        _shutdown_workers(workers)

        if mqtt_proxy is not None:
            try:
                mqtt_proxy.close()
            except Exception as ex:
                _logger.exception(ex)

        if mqtt_client is not None:
            try:
                mqtt_client.close()
            except Exception as ex:
                _logger.exception(ex)


def generate_json_schema_info(config_file: Optional[str]) -> str:
    text_blocks = []

    def append_text(text_block):
        text_blocks.append(text_block)

    def append_schema(text_block):
        text_blocks.append(json.dumps(text_block, indent=4, sort_keys=True))

    try:
        if not config_file:
            append_text(
                "The JSON schema output is supposed to contain also the worker extra settings, but therefore it needs a specific "
                "configuration. So please provide the configuration file.\n"
            )
            append_schema(ServiceConfigurator.generate_config_file_json_schema(None))
        else:
            service_config = ServiceConfigurator()
            service_config.read_config_file(config_file, skip_file_access_check=True)

            worker_instances_config = service_config.get_worker_instances_config()
            workers = WorkerFactory.create_workers(worker_instances_config)
            workers_extra_configs = WorkerFactory.extract_workers_settings_declarations(workers)

            append_schema(ServiceConfigurator.generate_config_file_json_schema(workers_extra_configs))

    except ValidationError as ex:
        append_text(
            "The JSON schema output is supposed to contain also the worker extra settings, but that is only possible "
            "if the base settings can be read flawlessly. Actually there is a problem reading the config file, so only "
            "the base JSON schema is shown.\n\nActual problem: {}\n".format(str(ex.message))
        )
        append_schema(ServiceConfigurator.generate_config_file_json_schema(None))

    return "\n".join(text_blocks)


if __name__ == '__main__':
    worker_bunch_main()  # exit codes must be handled by click!
