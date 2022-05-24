import sys
import os
import platform
from rook.exceptions import RookDependencyError

PLATFORM = sys.platform
CPYTHON = platform.python_implementation() == 'CPython'


class DummyExtension(object):
    pass


if PLATFORM in ('darwin', 'linux2', 'linux'):
    hook_installed = False
    original_os_fork = os.fork
    _fork = None

    if CPYTHON:
        try:
            import native_extensions
        except Exception as e:
            raise RookDependencyError(e)
    else:
        native_extensions = DummyExtension()

    native_extensions.python_fork_handler_called = 1

    def os_fork_hook():
        global _fork
        try:
            from .singleton import singleton_obj  # lgtm[py/cyclic-import]

            singleton_obj.pre_fork()
        except:  # can't risk leaking exceptions lgtm[py/catch-base-exception]
            pass

        # Set "called" flag, to be checked in the
        # pthread_atfork, and reset after
        native_extensions.python_fork_handler_called = 1
        pid = original_os_fork()
        native_extensions.python_fork_handler_called = 0

        try:
            from .singleton import singleton_obj  # lgtm[py/cyclic-import]

            if pid == 0:
                # child

                # Clean all Rook state
                singleton_obj.post_fork_clean()

                # Shutdown external API
                from . import interface
                interface.stop()

                # restore original fork
                os.fork = original_os_fork

                # At this point the rook is fully down
                if _fork:
                    interface.start()
            else:
                # parent
                singleton_obj.post_fork_recover()
        except:   # can't risk leaking exceptions lgtm[py/catch-base-exception]
            pass

        return pid

    def install_fork_handler(fork):
        global hook_installed, original_os_fork, _fork

        if hook_installed:
            return

        if CPYTHON:
            # due to occasional deadlocks in PyPy, pthread_atfork
            # functionality is disabled
            native_extensions.RegisterPreforkCallback()

        os.fork, hook_installed, _fork = os_fork_hook, True, fork

    def remove_fork_handler():
        global hook_installed, original_os_fork

        os.fork, hook_installed = original_os_fork, False

else:
    def install_fork_handler(fork):
        pass

    def remove_fork_handler():
        pass
