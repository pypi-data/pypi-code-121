# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from __future__ import print_function
import platform
import sys
import threading
import contrast
from contrast import __version__, AGENT_CURR_WORKING_DIR
from contrast.reporting import teamserver_messages
from contrast.agent import patch_controller, service_client, scope
from contrast.agent.request_context import RequestContext
from contrast.agent.assess.rules.response.xss import analyze_xss
from contrast.agent.assess.rules.response.analyze import analyze_response_rules
from contrast.agent.assess.preflight import update_preflight_hashes
from contrast.agent.assess.rules.providers.enable import enable_providers
from contrast.agent.middlewares.route_coverage.routes_mixin import RoutesMixin
from contrast.agent.settings import Settings
from contrast.agent.speedracer_input_analysis import get_input_analysis
from contrast.api.dtm_pb2 import AttackResult
from contrast.reporting import ReportingClient
from contrast.utils.decorators import cached_property
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)
from contrast.utils.decorators import log_time_cm
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils import inventory_utils
from contrast.utils.library_reader.library_reader import LibraryReader
from contrast.utils.loggers.logger import setup_agent_logger, setup_basic_agent_logger
from contrast.utils.timer import now_ms_float, now_ms
from contrast.utils.decorators import fail_loudly, fail_quietly
from contrast.assess_extensions import cs_str

if not contrast.telemetry_disabled():
    from contrast.agent.telemetry import Telemetry
else:
    Telemetry = None

# initialize a basic logger until config is parsed
logger = setup_basic_agent_logger()


class BaseMiddleware(RoutesMixin):
    """
    BaseMiddleware contains all the initial setup for the framework middlewares

    Requirements:

        1. It's callable
        2. It has call_with_agent
        3. It has call_without_agent

    Pre and post filter calls should not block the flow that this class has.

    Pre -> get_response -> post
    """

    _loaded = False
    app_name = ""  # This should be overridden by child classes

    DIAGNOSTIC_ENDPOINT = "/save-contrast-security-config"
    DIAGNOSTIC_ALLOWED_SERVER = "localhost"
    DIAGNOSTIC_ALLOWED_IP = "127.0.0.1"
    OVERRIDE_MESSAGE = (
        "A security filter prevented original response from being returned."
    )
    LOGS_SEPARATOR = "-" * 120

    def __init__(self):
        """
        If this method is called more than once per process, we use the _loaded
        flag to only run the following work once:
            - turning on service
            - library analysis thread initialization
            - turning on patches
            - hardcoded rule providers
            - scanning config rules

        the following work will be done every time:
            - any logging
            - attribute definition
            - loading common configuration
            - initializing settings
        """
        if BaseMiddleware._loaded:
            logger.warning(
                "Contrast Agent middleware initialized more than once per process."
            )

        # id will be different across processes but also for multiple middlewares
        # within the same process
        self.id = id(self)

        self.log_initialize()

        self.settings = None
        self.routes = {}

        if not self.initialize_settings(self.app_name):
            return

        if not self.settings.is_agent_config_enabled():
            logger.warning("Contrast Agent is not enabled.")
            return

        setup_agent_logger(self.settings.config)
        self.settings.config.log_config()

        if not BaseMiddleware._loaded:
            cs_str.init_contrast_scope_cvars()

        if not BaseMiddleware._loaded and not self.initialize_service_client():
            logger.error("Unable to initialize Contrast Agent.")
            return

        # This call must happen after initializing SR so we have all data to log
        self.log_environment()
        self.warn_for_misleading_config()

        self.reporting_client = (
            ReportingClient() if self.settings.config.is_service_bypassed else None
        )

        if self.reporting_client is not None:
            self.reporting_client.start()
            if not self.successful_startup_msgs():
                logger.error(
                    "Unable to initialize Contrast Agent.", direct_to_teamserver=1
                )
                return

        if not BaseMiddleware._loaded:
            self.initialize_libraries()

            patch_controller.enable_patches()

        if self.settings.is_assess_enabled():
            # For now agent runtime starts before config scanning
            # this will be reset when time_limit_threshold is reached,
            # it doesn't symbolize the total agent runtime for all time.
            self.settings.agent_runtime_window = now_ms()

            if not BaseMiddleware._loaded:
                enable_providers()
                self.scan_configs_in_thread()

        self.log_finish_initialize()
        # Starting telemetry must happen at the very end of initialization
        # so we have all the data to send in startup messages.
        if not BaseMiddleware._loaded and Telemetry is not None:
            contrast.TELEMETRY = Telemetry()
            contrast.TELEMETRY.start()

        self.first_request = True
        self.request_start_time = None
        self.request_path = None
        BaseMiddleware._loaded = True

    def successful_startup_msgs(self):
        server_start_msg = teamserver_messages.ServerStart()
        response = self.reporting_client.send_message(server_start_msg)
        if response is None:
            return False

        server_start_msg.process_response(response, self.reporting_client)

        app_start_msg = teamserver_messages.ApplicationStartup()
        response = self.reporting_client.send_message(app_start_msg)
        if response is None:
            return False

        app_start_msg.process_response(response, self.reporting_client)
        return True

    @fail_loudly("Unable to initialize Contrast Agent Settings.", return_value=False)
    def initialize_settings(self, app_name):
        """
        Initialize agent settings.

        Returns True on settings being initialized and False if any failure.
        """
        self.settings = Settings(app_name=app_name)
        return True

    def initialize_service_client(self):
        """
        Initialize connection to service.

        Returns True on service being initialized and False if any failure.
        """
        try:
            service_client.send_startup_messages()
        except Exception as e:
            # catches any exception including ContrastServiceException
            logger.error(e, exc_info=e)
            return False
        return True

    def warn_for_misleading_config(self):
        protect_enabled = self.settings.is_protect_enabled()
        assess_enabled = self.settings.is_assess_enabled()

        logger.info("Protect: %s", protect_enabled)
        logger.info("Assess: %s", assess_enabled)

        if protect_enabled and self.settings.config.get("assess.enable"):
            logger.warning("Protect is running but Assess is enabled in local config")
            logger.warning("Defaulting to Protect behavior only")

        if not protect_enabled and self.settings.config.get("protect.enable", True):
            logger.warning("Protect enabled in local config but disabled by Teamserver")

        if (
            self.settings.is_agent_config_enabled()
            and not protect_enabled
            and not assess_enabled
        ):
            logger.warning("Neither Protect nor Assess is running")

    def log_environment(self):
        """
        Log current working directory, python version and pip version
        """
        banner = f"{'-' * 50}ENVIRONMENT{'-' * 50}"
        logger.debug(banner)
        logger.debug("Current Working Dir: %s", AGENT_CURR_WORKING_DIR)
        logger.debug("Python Version: %s", sys.version)
        logger.debug("Framework Version: %s", self.settings.framework)
        logger.debug("Server Version: %s", self.settings.server)
        logger.debug("Contrast Python Agent Version: %s", __version__)
        logger.debug(
            "Contrast Service Version %s",
            self.settings.server_features.contrast_service,
        )
        logger.debug("Platform %s", platform.platform())

        try:
            import pip

            logger.debug("Pip Version: %s", pip.__version__)
        except Exception:
            pass

        logger.debug(banner)

    def initialize_libraries(self):
        """
        If enabled, read libraries from the application
        :return: True
        """
        if not self.settings.is_analyze_libs_enabled():
            return

        # Passing callback to send message due to a circular import issue, and a
        # deadlock occurring if something is imported inside of a function running in
        # this thread
        send_message_func = (
            self.reporting_client.add_message
            if self.reporting_client
            else service_client.send_messages
        )

        self.library_reader = LibraryReader(
            self.settings, send_message_func=send_message_func
        )
        self.library_reader.start_library_analysis_thread()

    def is_agent_enabled(self):
        """
        Agent is considered enabled if all of the following are true:
        1. config value for 'enable' is True (or empty, defaults to True)
            (meaning no errors during initialization process including initial
            connection to Speedracer)
        2. ServiceClient connection to Speedracer is True

        NOTE: If #3 is false (the connection to Speedracer is down at any time during
        the request cycle) then the agent is automatically disabled.
        """
        if self.settings is None:
            return False

        if not self.settings.is_agent_config_enabled():
            return False

        if not service_client.is_connected():
            try:
                service_client.send_startup_messages()
            except ContrastServiceException:
                return False

        return service_client.is_connected()

    def call_with_agent(self, *args):
        raise NotImplementedError("Must implement call_with_agent")

    def call_without_agent(self, *args):
        """
        The agent does not set context when this function is called so all other patches
        (e.g propagators) that check context shouldn't run.
        """
        logger.debug("Contrast Agent did not analyze request %s", self.request_path)

    def should_analyze_request(self, environ):
        """
        Determine if request should be analyzed based on configured settings.

        While returning different types of objects based on logic is not a good
        pattern, in this case it's an optimization that allows us to create
        the request context obj when we need it.

        :return: False or RequestContext instance
        """
        if not self.is_agent_enabled():
            logger.debug("Will not analyze request: agent disabled.")
            return False

        if self.settings.ignore_request(self.request_path):
            logger.debug("Will not analyze request: request meets exclusions.")
            return False

        from contrast.agent.assess import sampling

        context = RequestContext(environ)
        if sampling.enabled() and sampling.meets_criteria(context):
            logger.debug("Will not analyze request: request meets sampling.")
            return False

        return context  # equivalent to returning True

    def handle_ensure(self, context, request):
        """
        Method that should run for all middlewares AFTER every request is made.
        """
        if context is None:
            logger.error("Context not defined in middleware ensure")
            return

        with scope.contrast_scope():
            if self.settings.is_assess_enabled():
                # route discovery and storage needs to occur before sending messages
                self.handle_routes(context, request)

                logger.debug("Updating preflight hashes with route info")
                update_preflight_hashes(context)

            logger.debug("Sending final messages for reporting.")

            context.truncate_request_body()

            if self.settings.config.is_service_bypassed:
                for msg in self.final_ts_messages(context):
                    self.reporting_client.add_message(msg)
            else:
                final_messages = self.final_messages(context)
                service_client.send_messages(final_messages)

        self.first_request = False

    def final_ts_messages(self, context):
        messages = [
            teamserver_messages.ServerActivity(),
            teamserver_messages.Preflight(context.activity),
            teamserver_messages.Activity(context),
        ]

        # Currently we do not report an observed route if the route signature is empty.
        # As a team we've decided there isn't a meaningful default signature value
        # we can provide to customers. If a route doesn't show up in Contrast UI,
        # it may be due to its missing signature. In this scenario, we will have to work
        # with the customer directly to understand why the signature was not created.
        if self.settings.is_assess_enabled() and context.observed_route.signature:
            messages.append(teamserver_messages.ObservedRoute(context.observed_route))

        if self.first_request and self.settings.is_inventory_enabled():
            # ApplicationUpdate message only sent at first request once we have routes
            messages.append(teamserver_messages.ApplicationInventory(self.routes))

        return messages

    def final_messages(self, context):
        inventory_utils.append_db(context)

        final_messages = [
            context.server_activity,
            context.activity,
        ]

        # Currently we do not report an observed route if the route signature is empty.
        # As a team we've decided there isn't a meaningful default signature value
        # we can provide to customers. If a route doesn't show up in Contrast UI,
        # it may be due to its missing signature. In this scenario, we will have to work
        # with the customer directly to understand why the signature was not created.
        if self.settings.is_assess_enabled() and context.observed_route.signature:
            final_messages.append(context.observed_route)

        if self.first_request and self.settings.is_inventory_enabled():
            # ApplicationUpdate message only sent at first request once we have routes
            final_messages.append(service_client.build_update_message(self.routes))

        return final_messages

    def generate_security_exception_response(self):
        """
        Generate a response to be returned in the case of a SecurityException.

        Middlewares must override this method in order to provide the kind
        of response object that is expected by that framework.
        """
        raise NotImplementedError(
            "Middlewares must provide their own security response generator"
        )

    def handle_exception(self, exception):
        """
        Handle an exception being thrown especially if it is a SecurityException
        """
        logger.debug(
            "Handling %s raised in %s",
            exception.__class__.__name__,
            self.__class__.__name__,
        )
        if isinstance(exception, SecurityException):
            logger.info("%s: %s", exception.__class__.__name__, exception)
            logger.debug("Overriding response in Contrast Middleware")
            return self.generate_security_exception_response()

        logger.error("Reraising %r", exception)
        raise

    def prefilter(self, context):
        """
        Prefilter - AKA input analysis - is performed mostly in Speedracer but partly
        in the agent.

        This is PROTECT only.

        In this method we call on speedracer to do input analysis, which can result in:
        1. Speedracer finds an attack in which case we block the request
        2. Speedracer returns input analysis to use for later sink / infilter analysis,
            in which case we store it here in the request context.
        """
        if not self.settings.is_protect_enabled():
            return

        with log_time_cm("protect prefilter"):
            context.speedracer_input_analysis = get_input_analysis()
            self.agent_prefilter()

    def agent_prefilter(self):
        """
        Prefilter for any rules that do not yet use speedracer
        """
        with scope.contrast_scope():
            self.prefilter_defend()

    @fail_quietly("Failed to run prefilter protect.")
    def prefilter_defend(self):
        rules = self.settings.protect_rules
        logger.debug("PROTECT: Running Agent prefilter.")

        for rule in rules.values():
            is_prefilter = rule.is_prefilter()

            if is_prefilter:
                rule.prefilter()

    def postfilter(self, context):
        """
        For all postfilter enabled rules.
        """
        with log_time_cm("postfilter"):
            if self.settings.is_protect_enabled():
                self.postfilter_defend()

            if self.settings.is_assess_enabled():
                with scope.contrast_scope():
                    self.response_analysis(context)

    def _process_trigger_handler(self, handler):
        """
        Gather metadata about response handler callback for xss trigger node

        We need to check whether the response handler callback is an instance method or
        not. This affects the way that our policy machinery works, and it also affects
        reporting, so we need to make sure to account for the possibility that handler
        is a method of some class rather than a standalone function.

        This should be called by the `trigger_node` method in child classes.
        """
        module = handler.__module__
        class_name = ""

        if hasattr(handler, "__self__"):
            class_name = handler.__self__.__class__.__name__
            args = (handler.__self__,)
            instance_method = True
        else:
            args = ()
            instance_method = False

        return module, class_name, args, instance_method

    @cached_property
    def trigger_node(self):
        """
        Trigger node property used by assess reflected xss postfilter rule

        This must be overridden by child classes that make use of the reflected
        xss postfilter rule.
        """
        raise NotImplementedError("Children must define trigger_node property")

    @fail_loudly("Unable to do assess response analysis")
    def response_analysis(self, context):
        """
        Run postfilter for any assess rules. Reflected xss rule runs by default.
        May be overridden in child classes.

        If the response content type matches a allowed content type, do not run
        assess xss response analysis. This is because the security team
        considers reflected xss within these content types to be a false positive.
        """
        logger.debug("ASSESS: Running response analysis")

        analyze_xss(context, self.trigger_node)

        if not self.settings.response_scanning_enabled:
            return

        if self.reporting_client:
            analyze_response_rules(context, self.reporting_client)

    @fail_quietly("Failed to run postfilter protect.")
    def postfilter_defend(self):
        rules = self.settings.protect_rules
        logger.debug("PROTECT: Running Agent postfilter.")

        for rule in rules.values():
            if rule.is_postfilter():
                rule.postfilter()

    def check_for_blocked(self, context):
        """
        Checks for BLOCK events in case SecurityException was caught by app code

        This should be called by each middleware after the view is generated
        but before returning the response (it can be before or after
        postfilter).

        If we make it to this call, it implies that either no SecurityException
        occurred, or if one did occur, it was caught by the application. If we
        find a BLOCK here, it necessarily implies that an attack was detected
        in the application, but the application caught our exception. If the
        application hadn't caught our exception, we never would have made it
        this far because the exception would have already bubbled up to the
        middleware exception handler. So this is really our first and our last
        opportunity to check for this particular edge case.
        """
        for result in context.activity.results:
            if result.response == AttackResult.BLOCKED:
                msg = f"Rule {result.rule_id} threw a security exception"
                raise SecurityException(None, message=msg)

    def log_start_request_analysis(self):
        self.request_start_time = now_ms_float()

        logger.debug("Beginning request analysis", request_path=self.request_path)

    def log_end_request_analysis(self):
        request_end_time = now_ms_float()

        logger.debug(
            "Ending request analysis",
            request_path=self.request_path,
        )

        elapsed_time = request_end_time - self.request_start_time

        logger.debug(
            "elapsed time request analysis ms",
            elapsed_time=elapsed_time,
            request_path=self.request_path,
        )

    def log_initialize(self):
        logger.info(
            "Initializing Contrast Agent %s [id=%s]", self.__class__.__name__, self.id
        )

        logger.info("Contrast Python Agent Version: %s\n", __version__)

    def log_finish_initialize(self):
        logger.info(
            "Finished Initializing Contrast Agent %s [id=%s] \n\n%s\n",
            self.__class__.__name__,
            self.id,
            self.LOGS_SEPARATOR,
        )

    def scan_configs_in_thread(self):
        """
        Run config scanning rules for assess in a separate thread.

        Not all frameworks we support will necessarily have config scanning rules.
        These frameworks should not start a thread.
        """
        if hasattr(self, "_scan_configs"):
            logger.debug("Will start a thread to scan config rules.")
            scanner = threading.Thread(target=self._scan_configs)
            scanner.daemon = True
            scanner.start()
        else:
            logger.debug(f"No config scanning rules for {self.__class__.__name__}")
