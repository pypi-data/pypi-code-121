# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent import scope

from contrast.agent.request import Request
from contrast.agent.settings import Settings
from contrast.api.dtm_pb2 import Activity, ServerActivity, ObservedRoute

from contrast.extern import structlog as logging
from contrast.utils.digest_utils import Digest
from contrast.utils.decorators import cached_property, fail_quietly
from contrast.utils.string_utils import ensure_binary, truncate

logger = logging.getLogger("contrast")


class RequestContext(object):
    def __init__(self, environ):
        scope.enter_contrast_scope()

        self.request = Request(environ)

        dtm = self.request.get_dtm()
        self.activity = Activity()
        self.activity.http_request.CopyFrom(dtm)

        # For protect: store attacks made during a request to report at the end
        self.attacks = []
        self.server_activity = ServerActivity()

        self.speedracer_input_analysis = None
        self.do_not_track = False

        # to be populated with a RouteCoverage dtm instance
        self.current_route = None

        self.observed_route = ObservedRoute()
        self.database_info = []
        self.source_count = 0
        self.propagation_count = 0

        self.max_sources_logged = False
        self.max_propagators_logged = False

        scope.exit_contrast_scope()

    @cached_property
    @fail_quietly("Unable to compute request hash")
    def hash(self):
        """
        Generates the hash checksum for the request. Converts the request method, uri,
        param names and content length to CRC checksum and returns string representation

        :return: str
        """
        hasher = Digest()

        hasher.update(self.request.method)
        hasher.update(self.request.get_normalized_uri())
        for key in self.request.params:
            hasher.update(key)

        hasher.update(self.request.content_length)
        return hasher.finish()

    @property
    def stop_source_creation(self):
        """
        Compare `source_count` to `max_context_source_events` config option
        :return: true if source_count within this request is equal to or
                 greater than configured threshold for source creation
        """
        if self.max_sources_logged:
            return True

        threshold_reached = self.source_count >= Settings().max_sources
        if threshold_reached:
            logger.warning(
                "Will not create more sources in this request. %s sources reached",
                self.source_count,
            )
            self.max_sources_logged = True

        return threshold_reached

    @property
    def stop_propagation(self):
        """
        Compare `source_count` to `max_propagation_events` config option
        :return: true if propagation_count within this request is equal to or
                 greater than configured threshold for propagation
        """
        if self.max_propagators_logged:
            return True

        threshold_reached = self.propagation_count >= Settings().max_propagation
        if threshold_reached:
            logger.warning(
                "Will not propagate any more in this request. %s propagations reached.",
                self.propagation_count,
            )
            self.max_propagators_logged = True

        return threshold_reached

    @property
    def propagate_assess(self):
        # TODO: PYT-644 move this property of out this class?
        return Settings().is_assess_enabled() and not scope.in_scope()

    def source_created(self):
        """
        Increase the running count of sources created in this request
        """
        self.source_count += 1

    def propagated(self):
        """
        Increase the running count of propagations created in this request
        """
        self.propagation_count += 1

    def extract_response_to_context(self, response):
        """
        Append response to request context and populate the HttpResponse DTM

        :response: Subclass of BaseResponseWrapper
        """
        self.response = response

        if not Settings().response_scanning_enabled:
            return

        self.activity.http_response.response_code = response.status_code

        # From the dtm for normalized_response_headers:
        #   Key is UPPERCASE_UNDERSCORE
        #
        #   Example: Content-Type: text/html; charset=utf-8
        #   "CONTENT_TYPE" => Content-Type,["text/html; charset=utf8"]
        for key, values in response.headers.dict_of_lists().items():
            normalized_key = key.upper().replace("-", "_")
            response_headers = self.activity.http_response.normalized_response_headers
            response_headers[normalized_key].key = key
            response_headers[normalized_key].values.extend(values)

        self.activity.http_response.response_body_binary = ensure_binary(
            response.body or ""
        )

    def get_xss_findings(self):
        """
        Return a list of Finding obj of rule_id reflected-xss, if any exist in Activity
        """
        return [
            finding
            for finding in self.activity.findings
            if finding.rule_id == "reflected-xss"
        ]

    def truncate_request_body(self):
        # Request body is truncated to not overwhelm ContrastUI.
        raw_request_body = self.activity.http_request.request_body_binary
        self.activity.http_request.request_body_binary = truncate(
            raw_request_body, length=4096
        )
