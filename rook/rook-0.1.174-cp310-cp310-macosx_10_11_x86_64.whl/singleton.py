"""This module is in charge of managing the rook's module state.

The external interface for the module is Rook located in rook.rook."""

import os
import sys
import platform
import atexit
import uuid

# This must be the first import, otherwise enable_gevent_for_grpc will fail since grpc has already been imported
from rook.logger import logger

from rook.config import AgentComConfiguration, ShutdownConfig

from rook.com_ws.output_ws import Output

from .augs.augs_manager import AugsManager
from .trigger_services import TriggerServices
from .services.monitor.monitor_service import MonitorService

from rook.exceptions import RookInterfaceException, RookVersionNotSupported
from rook.com_ws.agent_com_ws import AgentCom
from rook.com_ws.command_handler import CommandHandler
from rook.serverless import on_lambda

try:
    from .atfork import install_fork_handler, remove_fork_handler  # lgtm[py/cyclic-import]
except ImportError:
    pass


class _Singleton(object):
    """This is singleton is the class managing the module.

    It should never be referred to directly, instead use obj in this module."""

    def __init__(self):
        """Initialize the object, sets member variables."""
        self._check_version_supported()

        logger.info("Initializing Rook under process-%d", os.getpid())

        self._id = None
        self._services_started = False

        self._monitor_service = None
        self._trigger_services = TriggerServices()
        self._command_handler = None
        self._aug_manager = None
        self._fork_handler = None

        self._agent_com = None

    def _start_trigger_services(self, _enable_monitor=True):
        """Start trigger services.

        Calling this method multiple times will have no effect.
        """
        # Don't double init services
        if self._services_started:
            return

        self._init_id()
        self._output = Output(self._id)

        if _enable_monitor and not on_lambda:
            self._monitor_service = MonitorService.get_instance()
            self._monitor_service.start()

        self._trigger_services.start()
        self._aug_manager = AugsManager(self._trigger_services, self._output)
        self._services_started = True

    def _init_id(self):
        self._id = uuid.uuid4().hex

    def _stop_trigger_services(self):
        if not self._services_started:
            return

        if self._monitor_service:
            self._monitor_service.stop()

        self._aug_manager = None
        self._trigger_services.close()

        self._services_started = False

    def get_trigger_services(self):
        return self._trigger_services

    def connect(self, token, host, port, proxy, tags=None, labels=None, async_start=False, fork=False, debug=False,
                _enable_monitor=True, throw_errors=False):
        """Connect to the Agent."""
        if self._agent_com:
            raise RookInterfaceException("Multiple connection attempts not supported!")

        if install_fork_handler:
            install_fork_handler(fork)

        install_fault_handler = debug or os.environ.get('ROOKOUT_ENABLE_SEGFAULT')
        if install_fault_handler is not None and install_fault_handler == '1':
            self._install_fault_handler()

        logger.debug("Initiating AgentCom-\t%s:%d", host, int(port))

        labels = labels or {}
        tags = tags or []

        self._start_trigger_services()
        self._agent_com = AgentCom(self._id, host, port, proxy, token, labels, tags, debug, not throw_errors)
        self._command_handler = CommandHandler(self._agent_com, self._aug_manager)
        self._output.set_agent_com(self._agent_com)
        self._agent_com.start()
        if async_start is False:
            self._agent_com.wait_for_ready(AgentComConfiguration.TIMEOUT)

    def flush(self):
        self._output.flush_messages()

    def stop(self):
        logger.debug("Shutting down")

        if self._agent_com is not None:
            self._agent_com.stop()
        self._agent_com = None

        self._stop_trigger_services()

    def restart(self, tags=None, labels=None):
        logger.info("Restarting agent: " + self._id)
        if not self._agent_com:
            raise RookInterfaceException("Could not restart connection since it was not started")

        self.flush()

        self._init_id()
        logger.info("New agent id is %s", self._id)

        self._output.set_agent_id(self._id)
        self._agent_com.update_info(self._id, tags, labels)

        self._agent_com.restart()

    def pre_fork(self):
        if self._agent_com is not None:
            # to avoid new child to write father's fd in single-threaded communication
            self._agent_com.stop()

        self._trigger_services.pre_fork()

    def post_fork_recover(self):
        if self._agent_com is not None:
            self._agent_com.restart()

        self._trigger_services.post_fork()

    def post_fork_clean(self):
        self._trigger_services.post_fork()

        self._command_handler = None

        if self._agent_com:
            self._agent_com.stop()
            self._agent_com = None

        self._stop_trigger_services()
        if remove_fork_handler:
            remove_fork_handler()

    @staticmethod
    def _check_version_supported():
        try:
            supported_platforms = ['pypy', 'cpython']
            supported_version = ['2.7', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10']

            current_platform = platform.python_implementation().lower()
            if current_platform not in supported_platforms:
                raise RookVersionNotSupported("Rook is not supported in this platform: " + current_platform)

            major, minor, _, _, _ = sys.version_info
            current_version = "{}.{}".format(major, minor)
            if current_version not in supported_version:
                raise RookVersionNotSupported("Rook is not supported in this python version: " + current_version)

        except Exception as e:
            import traceback
            traceback.print_exc()

            raise e

    @staticmethod
    def _install_fault_handler():
        major, _, _, _, _ = sys.version_info
        if major == 3:
            try:
                import faulthandler
                faulthandler.enable(file=sys.stderr, all_threads=True)
            except: # lgtm[py/catch-base-exception]
                logger.exception("Failed to install fault handler")


singleton_obj = _Singleton()


def exit_handler():
    try:
        try:
            ShutdownConfig.IS_SHUTTING_DOWN = True

            logger.info("Exit handler called - flushing and closing WebSocket")
            if singleton_obj._agent_com:
                singleton_obj.flush()
                singleton_obj._agent_com.stop()
        except:  # lgtm[py/catch-base-exception]
            logger.exception("Flush and close failed")
        logger.info("Exit handler finished")
    except:  # lgtm[py/catch-base-exception]
        pass


atexit.register(exit_handler)
