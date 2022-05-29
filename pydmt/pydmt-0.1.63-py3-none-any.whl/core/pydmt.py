import logging
from typing import List, Dict

import os

from pydmt.api.builder import Builder
from pydmt.core.cache import Cache
from pydmt.utils.filesystem import copy_mkdir
from pydmt.utils.digest import sha1_file
from pydmt.configs import ConfigFlow
from pydmt.static import LOGGER_NAME


class BuildProcessStats:
    def __init__(self):
        self.builder_fail = []
        self.builder_ok = []
        self.copy_missing = []
        self.copy_sha1 = []
        self.nop = []

    def add_copy_missing(self, filename: str, object_name: str):
        self.copy_missing.append((filename, object_name))

    def get_copy_missing(self):
        return len(self.copy_missing)

    def add_copy_sha1(self, filename: str, object_name: str):
        self.copy_sha1.append((filename, object_name))

    def add_nop(self, filename: str, object_name: str):
        self.nop.append((filename, object_name))

    def get_nop(self):
        return len(self.nop)

    def add_builder_ok(self, builder: Builder):
        self.builder_ok.append(builder)

    def add_builder_fail(self, builder: Builder, e: Exception):
        self.builder_fail.append((builder, e))

    def get_builder_ok(self):
        return len(self.builder_ok)

    def get_builder_fail(self):
        return len(self.builder_fail)

    def get_os_error_code(self) -> int:
        if len(self.builder_fail) > 0:
            return 1
        return 0


class PyDMT:
    def __init__(self):
        self.builders: List[Builder] = []
        self.target_to_builder: Dict[str, Builder] = {}
        self.cache = Cache()

    def build_by_builder(self, builder: Builder, stats: BuildProcessStats):
        """ run one builder, return statistics about the run """
        logger = logging.getLogger(LOGGER_NAME)
        target_signature = builder.get_signature()
        logger.debug(f"examining [{builder.get_name()}]")
        if self.cache.list_sig_ok(target_signature):
            logger.debug(f"verifying [{builder.get_name()}]")
            file_bad = 0
            file_correct = 0
            file_missing = 0
            file_total = 0
            list_filename = self.cache.get_list_filename(target_signature)
            for object_name, signature in Cache.iterate_objects(list_filename):
                filename = self.cache.get_object_filename(signature)
                if os.path.isfile(object_name):
                    object_name_signature = sha1_file(object_name)
                    if object_name_signature != signature:
                        logger.debug(f"file [{object_name}] is incorrect. Getting from cache.")
                        copy_mkdir(filename, object_name)
                        stats.add_copy_sha1(filename, object_name)
                        file_bad += 1
                    else:
                        logger.debug(f"file [{object_name}] is up to date")
                        stats.add_nop(filename, object_name)
                        file_correct += 1
                else:
                    logger.debug(f"file [{object_name}] is missing. Getting from cache.")
                    copy_mkdir(filename, object_name)
                    stats.add_copy_missing(filename, object_name)
                    file_missing += 1
                file_total += 1
            if file_bad > 0 or file_missing > 0:
                logger.debug(f"Retrieved {file_total} files from cache")
                logger.debug(f"(bad/correct/missing = {file_bad}/{file_correct}/{file_missing}")
            else:
                logger.debug(f"ok [{builder.get_name()}]")
        else:
            logger.debug(f"running [{builder.get_name()}]")
            print(f"{builder.get_name()}: [{builder.get_targets_as_string()}]...", end="", flush=True)
            # this is one of the rare cases in which we really want to catch all exceptions.
            # pylint: disable=broad-except
            # noinspection PyBroadException
            try:
                builder.build()
            except Exception as e:
                print("FAIL")
                logger.exception("exception")
                stats.add_builder_fail(builder, e)
                return False
            print("OK")
            stats.add_builder_ok(builder)

            d = {}
            for signature, target in builder.yield_results():
                self.cache.save_object_by_signature(signature, target)
                d[target] = signature
            self.cache.save_list_by_signature(target_signature, d)
        return True

    def build_by_target(self, target: str, stats: BuildProcessStats) -> None:
        b = self.target_to_builder[target]
        self.build_by_builder(b, stats)

    def build_by_targets(self, targets: List[str], stats: BuildProcessStats) -> None:
        for target in targets:
            self.build_by_target(target, stats)

    def build_all(self) -> BuildProcessStats:
        """
        Build all the targets, very high level method
        TODO: order builders by depenencies and do this multi-core
        :return: statistics about the build
        """
        stats = BuildProcessStats()
        for builder in self.builders:
            res = self.build_by_builder(
                builder=builder,
                stats=stats,
            )
            if not res and ConfigFlow.stop_after_error:
                return stats
        return stats

    def clean_all(self) -> None:
        """
        Clean all targets
        """
        for builder in self.builders:
            for target in builder.get_targets():
                target.remove()

    def add_builder(self, b: Builder) -> None:
        self.builders.append(b)
        for target in b.get_targets():
            self.target_to_builder[target] = b
