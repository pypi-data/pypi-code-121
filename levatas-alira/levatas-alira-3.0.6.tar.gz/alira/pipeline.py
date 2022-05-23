import os
import logging
import yaml
import sys
import importlib.util
import redis
import re

from rq import Queue, Retry
from importlib import import_module

from alira.instance import Instance
from alira.modules.module import InternalError
from alira.store import Store

rq_worker_logger = logging.getLogger("rq.worker")

PIPELINE_FILENAME = "pipeline.yml"
PIPELINE_PYTHON_FILENAME = "pipeline.py"


class Pipeline(object):
    def __init__(
        self,
        pipeline_configuration: any = None,
        configuration_directory: str = None,
        store_configuration: dict = None,
        redis_server: str = None,
        asynchronous: bool = True,
        **kwargs,
    ):
        self.kwargs = kwargs

        self.configuration_directory = configuration_directory or os.path.abspath(
            os.getcwd()
        )
        self.store_configuration = store_configuration
        self.redis_server = redis_server or "redis://localhost:6379/"
        self.asynchronous = asynchronous

        # We are going to read the pipeline identifier and the list of
        # modules from the pipeline.yml file.
        self.pipeline_id = None
        self.modules = None
        self.dependencies = None

        self._load_pipeline_configuration(pipeline_configuration)

    def run(self, data: dict) -> Instance:
        instance = Instance.create(data)

        store = Store.configure(
            configuration_directory=self.configuration_directory,
            store_configuration=self.store_configuration,
        )
        store.put(instance)

        if self.asynchronous:
            redis_connection = redis.from_url(self.redis_server)
        else:
            import fakeredis

            redis_connection = fakeredis.FakeStrictRedis()

        queue = Queue(
            self.pipeline_id,
            connection=redis_connection,
            is_async=self.asynchronous,
        )

        job = None
        for module in self.modules:
            module_signature = f"{module.__module__}.{module.__class__.__name__}"

            logging.info(f"Scheduling module {module_signature}...")

            arguments = {} if job is None else {"depends_on": job}

            if hasattr(module, "schedule"):
                max_retries, *interval = module.schedule
                retry = Retry(max=max_retries, interval=interval)
                arguments["retry"] = retry

            job = queue.enqueue(
                Pipeline.run_module,
                module=module,
                module_signature=module_signature,
                instance=instance,
                dependencies=self.dependencies,
                store_configuration=self.store_configuration,
                pipeline_id=self.pipeline_id,
                configuration_directory=self.configuration_directory,
                **arguments,
            )

        # At this point, we need to refresh the store to load any changes that
        # might have happened during the execution of the pipeline.
        store.refresh()

        return store.get(instance.id) or instance

    @classmethod
    def run_module(
        self,
        module,
        module_signature,
        instance,
        dependencies,
        store_configuration,
        pipeline_id,
        configuration_directory,
    ):
        rq_worker_logger.info(f"Running module {module_signature}...")

        store = Store.configure(
            configuration_directory=configuration_directory,
            store_configuration=store_configuration,
        )

        Pipeline.load_pipeline_python_file(pipeline_id, configuration_directory)

        instance = store.get(instance.id) or instance
        rq_worker_logger.debug(f"Input instance: {instance.to_dict()}")
        rq_worker_logger.debug(f"Dependencies: {dependencies}")

        module_name = (
            module.module_id if hasattr(module, "module_id") else module_signature
        )

        try:
            result = module.run(instance, **dependencies)

            if result is None:
                return None

            module_output = {module_name: result}
        except TypeError as e:
            error = f"Unable to run module: {e}"
            rq_worker_logger.exception(error)
            module_output = {module_name: error}
        except InternalError as e:
            error = f"Internal Exception: {e}"
            rq_worker_logger.exception(error)
            module_output = {module_name: error}

        instance = store.get(instance.id) or instance
        instance.properties.update(module_output)
        store.put(instance)

        rq_worker_logger.debug(f"Output instance: {instance.to_dict()}")
        return module_output

    @classmethod
    def load_pipeline_python_file(self, pipeline_id, configuration_directory):
        python_filename = os.path.join(
            configuration_directory, PIPELINE_PYTHON_FILENAME
        )
        if os.path.isfile(python_filename):
            rq_worker_logger.info(
                f"Adding {PIPELINE_PYTHON_FILENAME} content to system path..."
            )

            module_name = f"{pipeline_id}.pipeline"

            try:
                spec = importlib.util.spec_from_file_location(
                    module_name, python_filename
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                logging.info(f"Loaded {python_filename} as module {module_name}")
            except Exception:
                logging.exception(
                    f"There was an error loading {python_filename} "
                    f"as module {module_name}"
                )

    def _load_pipeline_configuration(self, pipeline_configuration):
        if pipeline_configuration is None:
            pipeline_configuration = os.path.join(
                self.configuration_directory, PIPELINE_FILENAME
            )

        if hasattr(pipeline_configuration, "read"):
            pipeline_configuration = self._load_pipeline_configuration_from_stream(
                pipeline_configuration
            )
        else:
            pipeline_configuration = self._load_pipeline_configuration_from_file(
                pipeline_configuration
            )

        self.pipeline_id = pipeline_configuration.get("name", None)
        if self.pipeline_id is None:
            raise ValueError(
                "The name of the pipeline should be specified as part of "
                "the configuration."
            )

        self.modules = list(
            self._load_modules(pipeline_configuration, "pipeline").values()
        )
        self.dependencies = self._load_modules(pipeline_configuration, "dependencies")

    def _load_modules(self, pipeline_configuration, section: str):
        result = {}
        for section_data in pipeline_configuration.get(section, []):
            try:
                module_path, _, module_name = section_data["module"].rpartition(".")
                module = getattr(import_module(module_path), module_name)
                logging.info(f"Loaded module {module_path}.{module_name}")
            except ModuleNotFoundError as e:
                raise RuntimeError(
                    f"Unable to load module {module_path}.{module_name}"
                ) from e

            arguments = {
                "pipeline_id": self.pipeline_id,
                "configuration_directory": self.configuration_directory,
            }

            for argument_id, argument in section_data.items():
                if argument_id == "module":
                    continue

                arguments[argument_id] = argument

            arguments.update(self.kwargs)

            # Every module should have a `reference`. This will be the configured
            # `module_id` or a snake_case name based on the module name.
            if "module_id" in arguments:
                reference = arguments["module_id"]
            else:
                reference = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", module_name)
                reference = re.sub("([a-z0-9])([A-Z])", r"\1_\2", reference).lower()
                while reference in result:
                    reference += "_"

            result[reference] = module(**arguments)

        return result

    def _load_pipeline_configuration_from_stream(self, pipeline_configuration):
        try:
            return yaml.safe_load(pipeline_configuration.read())
        except Exception as e:
            logging.exception(e)
            raise RuntimeError("Unable to load pipeline configuration") from e

    def _load_pipeline_configuration_from_file(self, pipeline_configuration):
        logging.info(f"Loading pipeline configuration from {pipeline_configuration}...")

        try:
            with open(pipeline_configuration) as file:
                return yaml.load(file.read(), Loader=yaml.FullLoader)
        except Exception as e:
            logging.exception(e)
            raise RuntimeError(
                "Unable to load pipeline configuration from "
                f"file {pipeline_configuration}"
            ) from e
