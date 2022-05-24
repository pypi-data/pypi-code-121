import sys
import time
import threading

import six
import os
import inspect
import site
import imp
import hashlib

from six.moves import builtins

from rook.logger import logger

from rook.config import ImportServiceConfig

from rook.serverless import on_lambda

from rook.exceptions import RookDependencyError, RookSourceFilePathSuggestion

from rook.file_utils import FileUtils

from rook.processor.error import Error

_SUPPORTED_PY_FORMATS = ['.py', '.pyc']

_BLACKLISTED_PATHS = []

_OLD_IMPORT_FUNC = builtins.__import__


# only used in tests
def set_old_import_func(import_func):
    global _OLD_IMPORT_FUNC
    current = _OLD_IMPORT_FUNC
    _OLD_IMPORT_FUNC = import_func
    return current


class CountingImportLock(object):
    """
    When locked, only this thread can import (so all imports are guaranteed to have completed,
                                              and there are no partially initialized modules in sys.modules)
    The import lock is used here because:
    (1) it's reentrant, so we won't block user threads when they already hold it
    (2) it guarantees that if it's locked, no imports are partially complete
    (3) generally speaking, if you use more than 1 lock, there's the potential for deadlocks:
        locking (A) then (B) and another thread locking (B) then (A)
        This is an inherent risk in an import hook because the import lock is locked by Python itself,
        so using _any other lock_can  result in deadlocks
    """
    def __init__(self):
        self._count = 0

    def __enter__(self):
        imp.acquire_lock()
        self._count += 1

    def __exit__(self, *args, **kwargs):
        self._count -= 1
        imp.release_lock()

    def get_recursion_count(self):
        return self._count


class ImportService(object):

    NAME = "Import"

    def __init__(self, bdb_location_service):
        self._bdb_location_service = bdb_location_service

        self._modules = sys.modules.copy()
        self._path_cache = {}
        self._post_import_notifications = {}

        self._thread = None
        self._quit = False

        self.file_utils = FileUtils()

        external_paths = [sys.prefix]

        if hasattr(sys, 'base_prefix') and sys.base_prefix not in external_paths:
            external_paths += [sys.base_prefix]

        if hasattr(site, 'getsitepackages') and hasattr(site, 'getsitepackages') and hasattr(site, 'getusersitepackages'):
            external_paths += site.getsitepackages() + [site.getuserbase() + site.getusersitepackages()]

        self.external_paths = [os.path.normcase(os.path.realpath(external_path))
                               for external_path in external_paths]

        # pyenv messes up sys.path, so we ignore everything under it's folder
        for path in self.external_paths:
            pyenv_offset = path.find('.pyenv')
            if pyenv_offset != -1:
                pyenv_directory = path[:pyenv_offset + len('.pyenv') + 1]
                self.external_paths += [pyenv_directory]
                break

        # If we are (heuristicly) worried we missed anything, add "catch-alls"
        if len(self.external_paths) < 3:
            logger.debug("Missing getsitepackages, adding heuristics")
            self.external_paths += ['site-packages', 'site-python']

        logger.debug("External paths are " + str(self.external_paths))

        if on_lambda():
            _BLACKLISTED_PATHS.extend(['/var/task/flask', '/var/task/chalice'])

        import platform
        if platform.system() != 'Windows' and ImportServiceConfig.USE_IMPORT_HOOK:
            platform = platform.python_implementation().lower()

            def import_hook(*args, **kwargs):
                """
                Declared here to make it obvious that you can't replace the function by monkeypatching -
                the C extension will always reference the function set with SetImportHook.
                """
                __rookout__tracebackhide__ = True
                # Locking the global import lock here extends the section for which it is locked -
                # we don't want the import hook to be called from two threads simultaneously,
                # but the scope in which the import lock is held might only encompass the call to the original
                # __import__. The import lock is re-entrant, so it's OK for us to lock it and then for Python
                # to lock it again.
                with import_hook.import_lock:
                    result = _OLD_IMPORT_FUNC(*args, **kwargs)

                    # TODO - review if we can process the module being loaded regardless instead of evaluating the full list
                    try:
                        # if the recursion count is > 1,
                        # then this call to import_hook is a nested import, which means that the parent
                        # import has not finished executing its code yet, but it's already in sys.modules.
                        # if we evaluate now, we will try to place BPs in the module before it finished executing,
                        # potentially resulting in CodeNotFound.
                        if import_hook.import_lock.get_recursion_count() == 1:
                            self.evaluate_module_list()
                    except:  # lgtm[py/catch-base-exception]
                        pass

                    return result
            # this must be a reentrant lock - imports can cause other imports
            import_hook.import_lock = CountingImportLock()

            if platform == "cpython":
                try:
                    import native_extensions
                except Exception as e:
                    raise RookDependencyError(e)

                logger.debug('Enabling native import hook')
                native_extensions.SetImportHook(import_hook)
                # atomic swap
                builtins.__import__ = native_extensions.CallImportHookRemovingFrames
            elif platform == "pypy":
                import __pypy__
                logger.debug('Enabling pypy import hook')
                # atomic swap
                builtins.__import__ = __pypy__.hidden_applevel(import_hook)
            else:
                # assertion should never be reached, singleton.py checks platform support
                raise AssertionError("Unsupported platform")
        else:
            self._thread = threading.Thread(target=self._query_thread,
                                            name=ImportServiceConfig.THREAD_NAME)
            self._thread.daemon = True
            self._thread.start()

    def close(self):
        if _OLD_IMPORT_FUNC:
            builtins.__import__ = _OLD_IMPORT_FUNC

        if self._thread:
            self._quit = True

            # If threading was monkey patched by gevent waiting on thread will likely throw an exception
            try:
                from gevent.monkey import is_module_patched
                if is_module_patched("threading"):
                    time.sleep(ImportServiceConfig.SYS_MODULES_QUERY_INTERVAL)
            except Exception:  # Nothing we can do here but join as usual
                pass

            self._thread.join()

    def register_post_import_notification(self, location):
        filepath = location.filename
        filename = os.path.basename(filepath) if filepath else None

        # Register notification for future loads
        self._post_import_notifications[location.aug_id] = location

        # declaring filenames blacklist for avoiding setting multiple callbacks on the same aug
        modules_blacklist = []
        match_found = False
        file_hashes = {}
        with CountingImportLock():
            # Attempt to satisfy location using known modules
            for module_key, module_object in self._modules.items():
                # Get module details and check if it matches
                module_filename = self._get_module_path(module_object)

                # If module is not valid, ignore
                if not self._is_valid_module(module_object, module_filename):
                    continue

                if filename == os.path.basename(module_filename):
                    file_content = self.file_utils.get_safe_file_contents(module_object)
                    if file_content:
                        file_hash = hashlib.sha256(file_content).hexdigest()
                        file_hashes[file_hash] = inspect.getsourcefile(module_object)

                if module_filename:
                    module_identifier = self._get_module_identifier(module_object, module_filename)

                    if module_identifier not in modules_blacklist:
                        if self._does_module_match_notification(module_filename, location, self.external_paths):
                            match_found = True
                            modules_blacklist.append(module_identifier)
                            location.module_found(module_object)
                    else:
                        logger.warn("Found duplicated occurrences of the same module that are matching the aug, "
                                    "can cause the aug to not be triggered. aug_ig: %s, module_key: %s, module_path: %s"
                                    % (location.aug_id, module_key, module_filename))

        if not match_found:
            if location.file_hash in file_hashes:
                location.send_warning(Error(exc=RookSourceFilePathSuggestion(filepath, file_hashes[location.file_hash])))

    def remove_aug(self, aug_id):
        location = self._post_import_notifications.pop(aug_id, None)
        if location is None:
            return

        location.set_removed()

    def clear_augs(self):
        # This does not require a lock - `notifications` may be added to or removed from in a different thread
        # while we still haven't replaced it with an empty dict(),
        # but `notifications` is just a pointer to the same dict object pointed to by
        # `_post_import_notifications`. Once we do replace `_post_import_notifications`
        # with a new dict, we can be sure that no more notifications will be added.
        # At that point, it's safe to iterate over `notifications` and remove all notifications.
        notifications = self._post_import_notifications
        self._post_import_notifications = dict()
        for location in six.itervalues(notifications):
            location.set_removed()

    def pre_fork(self):
        CountingImportLock().__enter__()

    def post_fork(self):
        try:
            CountingImportLock().__exit__()
        except RuntimeError:
            # This is a bit of a heck as we don't seem to hold import lock in the child.
            # See the TODO about migrating away from the import lock.
            pass

    def _is_valid_module(self, module_object, module_filename):
        return module_filename and os.path.splitext(module_filename)[1] in _SUPPORTED_PY_FORMATS and \
            module_object and inspect.ismodule(module_object) and hasattr(module_object, '__file__')

    def _query_thread(self):
        logger.debug('Starting ImportService thread')
        self._bdb_location_service.ignore_current_thread()

        while not self._quit:
            try:
                with CountingImportLock():
                    self.evaluate_module_list()
            except:  # lgtm[py/catch-base-exception]
                if logger:
                    logger.exception("Error while evaluating module list")

            # time can be None if interpreter is in shutdown
            if not time:
                return
            time.sleep(ImportServiceConfig.SYS_MODULES_QUERY_INTERVAL)

    def evaluate_module_list(self):
        try:
            # No new modules
            if len(self._modules) == len(sys.modules):
                return

            # Get a fresh list
            modules = sys.modules.copy()

            if self._post_import_notifications:
                # self._modules is only replaced (it's immutable - a frozenset), so there's no need to copy it here,
                # just keep a reference to the current self._modules so we don't start working on a different set
                # mid-loop
                old_modules = self._modules

                # For everybody not in the old list, check notifications
                for module_name, module in six.iteritems(modules):
                    module_filename = self._get_module_path(module)
                    if module_name not in old_modules.keys() and self._is_valid_module(module, module_filename):
                        self._notify_of_new_module(module, module_filename)

            # Update the "old" list
            self._modules = modules

        except Exception:
            logger.exception("Exception in ImportService")

    def _notify_of_new_module(self, module_object, module_filename):
        self._trigger_all_notifications_for_module(module_filename, module_object)

    def _trigger_all_notifications_for_module(self, module_filename, module):
        if module_filename:
            for aug_id, location in six.iteritems(self._post_import_notifications.copy()):
                if self._does_module_match_notification(module_filename, location,
                                                        self.external_paths):
                    try:
                        location.module_found(module)
                    except:  # lgtm[py/catch-base-exception]
                        logger.exception("Error on module load callback")
                elif os.path.basename(location.filename) == os.path.basename(module_filename):
                    file_content = self.file_utils.get_safe_file_contents(module)
                    if file_content:
                        file_hash = hashlib.sha256(file_content).hexdigest()
                        if location.file_hash == file_hash:
                            location.send_warning(Error(exc=RookSourceFilePathSuggestion(location.filename, module_filename)))

    def _get_module_path(self, module):
        if module is None or not hasattr(module, '__name__') or not hasattr(module, '__file__'):
            return None
        result = self._path_cache.get(module.__name__)

        if result is not None:
            return result

        if module:
            try:
                path = inspect.getsourcefile(module)
                if not path:
                    if module.__file__.endswith('.pyc'):
                        path = module.__file__.replace('.pyc', '.py')
            except Exception:
                return None

            if path:
                result = os.path.normcase(os.path.abspath(path))
                self._path_cache[module.__name__] = result
                return result

        return None

    @staticmethod
    def _get_module_identifier(module, filename):
        module_identifier = str(filename)
        module_identifier += "#" if not hasattr(module, '__name__') else str(module.__name__)
        module_identifier += "#" if not hasattr(module, '__loader__') else str(type(module.__loader__))
        module_identifier += "#" if not (hasattr(module, '__loader__') and hasattr(module.__loader__, 'path')) \
            else str(module.__loader__.path)

        return module_identifier

    @staticmethod
    def is_black_listed_path(path):
        for blacklisted_path in _BLACKLISTED_PATHS:
            if path.startswith(blacklisted_path):
                return True
        return False

    @staticmethod
    def _does_module_match_notification(module_filename, location, external_paths):
        if not location.include_externals:
            for external_path in external_paths:
                if external_path in module_filename:
                    return False

        if location.filename and ImportService.path_contains_path(module_filename, location.filename) and \
                        not ImportService.is_black_listed_path(module_filename):
            return True
        else:
            return False

    @staticmethod
    def path_contains_path(full_path, partial_path):
        if full_path.endswith(partial_path):
            return len(full_path) == len(partial_path) or full_path[-len(partial_path)-1] in ('/', '\\')
        else:
            return False
