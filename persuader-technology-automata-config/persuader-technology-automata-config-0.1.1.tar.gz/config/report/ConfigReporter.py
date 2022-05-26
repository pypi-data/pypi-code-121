import logging

from missingrepo.Missing import Missing
from missingrepo.repository.MissingRepository import MissingRepository


class ConfigReporter:

    def __init__(self, missing_repository: MissingRepository):
        self.log = logging.getLogger(__name__)
        self.missing_repository = missing_repository
        self.ignored_check_func = None
        self.local_missing_cache = self.init_local_missing_cache()

    def init_local_missing_cache(self):
        all_missing = self.missing_repository.retrieve()
        if len(all_missing) == 0:
            return {}
        return dict([(missing.missing, missing) for missing in all_missing])

    def set_ignored_check_func(self, func):
        self.ignored_check_func = func

    def report_missing(self, missing: Missing, func=None):
        if self.is_already_ignored(missing) or self.is_already_missing(missing):
            return
        self.local_missing_cache[missing.missing] = missing
        if func is not None:
            func()

    def is_already_ignored(self, missing: Missing) -> bool:
        return False if self.ignored_check_func is None else self.ignored_check_func(missing)

    def is_already_missing(self, missing: Missing):
        return missing.missing in self.local_missing_cache

    def delay_missing_storing(self):
        self.copy_local_missing_cache_to_repository()

    def copy_local_missing_cache_to_repository(self):
        multiple_missing = list(self.local_missing_cache.values())
        self.log.debug(f'Delayed storing missing:[{len(multiple_missing)}]')
        self.missing_repository.store(multiple_missing)
