from typing import Dict

from worker_bunch.worker.worker import Worker
from worker_bunch.worker.worker_config import WorkerSettingsDeclaration


class WorkerFactory:

    PREDEFINED_WORKERS = {
        "AstralTimesPublisher": "worker_bunch.astral_times.astral_times_publisher.AstralTimesPublisher",
        "DatabaseWorker": "worker_bunch.database.database_worker.DatabaseWorker",
    }

    @classmethod
    def _check_class(cls, candidate):
        if not isinstance(candidate, Worker):
            if candidate:
                class_info = candidate.__class__.__module__ + '.' + candidate.__class__.__name__
            else:
                class_info = 'None'
            class_target = Worker.__module__ + '.' + Worker.__name__
            raise TypeError("{} is not of type {}!".format(class_info, class_target))

    @classmethod
    def resolve_import(cls, path: str) -> Worker.__class__:
        delimiter = path.rfind(".")
        class_name = path[delimiter + 1:len(path)]
        module_name = __import__(path[0:delimiter], globals(), locals(), [class_name])
        return getattr(module_name, class_name)

    @classmethod
    def create_worker(cls, worker_name: str, class_path: str):
        try:
            worker_class = cls.resolve_import(class_path)
            worker = worker_class(worker_name)
            cls._check_class(worker)
            return worker
        except Exception as ex:
            print('could not create worker "{}"! {}'.format(class_path, ex))
            raise

    @classmethod
    def create_workers(cls, config) -> Dict[str, Worker]:
        workers = {}
        for worker_name, class_path in config.items():

            predefined_class_paths = cls.PREDEFINED_WORKERS.get(class_path)
            if predefined_class_paths:
                class_path = predefined_class_paths

            if worker_name and class_path:
                workers[worker_name] = cls.create_worker(worker_name, class_path)
        return workers

    @classmethod
    def extract_workers_settings_declarations(cls, workers: Dict[str, Worker]) -> Dict[str, WorkerSettingsDeclaration]:
        settings_declarations = {}
        for worker_name, worker in workers.items():
            settings_declarations[worker_name] = WorkerSettingsDeclaration(
                settings_schema=worker.get_partial_settings_schema(),
                required=worker.make_partial_settings_required(),
            )
        return settings_declarations
