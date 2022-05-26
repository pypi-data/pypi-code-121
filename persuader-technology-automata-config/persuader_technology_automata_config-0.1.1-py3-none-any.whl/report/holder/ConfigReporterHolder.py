from missingrepo.repository.MissingRepository import MissingRepository

from config.report.ConfigReporter import ConfigReporter


class ConfigReporterHolder:
    __instance = None

    def __new__(cls, options=None):
        if cls.__instance is None:
            missing_repository = MissingRepository(options)
            cls.__instance = ConfigReporter(missing_repository)
        return cls.__instance

    @staticmethod
    def set_ignore_check_func(func):
        ConfigReporterHolder.__instance.set_ignored_check_func(func)

    @staticmethod
    def delay_missing_storing():
        ConfigReporterHolder.__instance.delay_missing_storing()
