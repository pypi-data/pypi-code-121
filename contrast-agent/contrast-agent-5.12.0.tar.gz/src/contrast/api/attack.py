# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.api.dtm_pb2 import AttackResult as AttackDtm, HttpRequest, UserInput
from contrast.agent.settings import Settings
from contrast.utils.decorators import fail_quietly
from contrast.utils.string_utils import ensure_string
from contrast.utils.timer import now_ms
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class Attack(object):
    """
    Wrapper around api.dtm_pb2.AttackResult
    """

    def __init__(self, attack_dtm: AttackDtm, request: HttpRequest):
        self.attack_dtm = attack_dtm
        self.rule_id = attack_dtm.rule_id
        self.request_dtm = request
        self.path, _, self.querystring = request.raw.partition("?")
        self.response = self.attack_dtm.response
        self.blocked = self.response == AttackDtm.BLOCKED
        self.start_time_ms = contrast.CS__CONTEXT_TRACKER.current().request.timestamp_ms

    def _convert_details(self, sample):
        rule_class = Settings().protect_rules.get(self.rule_id)
        if not rule_class:
            return {}
        return rule_class.sample_dtm_to_json(sample)

    def _convert_samples(self):
        DOCUMENT_TYPES = {
            0: "NORMAL",
            1: "JSON",
            2: "XML",
        }

        return [
            {
                "blocked": self.blocked,
                "input": {
                    "documentPath": sample.user_input.path,
                    "documentType": DOCUMENT_TYPES.get(sample.user_input.document_type),
                    "filters": [item for item in sample.user_input.matcher_ids],
                    "name": sample.user_input.key,
                    "time": sample.timestamp_ms,
                    "type": UserInput.InputType.Name(sample.user_input.input_type),
                    "value": sample.user_input.value,
                },
                "details": self._convert_details(sample),
                "request": {
                    "body": ensure_string(self.request_dtm.request_body_binary),
                    # the WSGI environ supports only one value per request header. However
                    # the server decides to handle multiple headers, we're guaranteed to
                    # have only unique keys in request.request_headers (since we iterate
                    # over webob's EnvironHeaders). Thus, each value list here is length-1.
                    "headers": {
                        k: [v] for k, v in self.request_dtm.request_headers.items()
                    },
                    "method": self.request_dtm.method,
                    "parameters": {
                        h.key: list(h.values)
                        for h in self.request_dtm.normalized_request_params.values()
                    },
                    "port": self.request_dtm.receiver.port,
                    "protocol": self.request_dtm.protocol,
                    "queryString": self.querystring,
                    "uri": self.path,
                    "version": self.request_dtm.version,
                },
                "stack": self._convert_stacks(sample.stack_trace_elements),
                "timestamp": {
                    "start": sample.timestamp_ms,  # in ms
                    # TODO: PYT-2292  #  / 1000,  # in secs
                    "elapsed": (now_ms() - sample.timestamp_ms),
                },
            }
            for sample in self.attack_dtm.samples
        ]

    def _convert_stacks(self, stacks_dtm):
        return [
            {
                "declaringClass": stack.declaring_class,
                "methodName": stack.method_name,
                "fileName": stack.file_name,
                "lineNumber": stack.line_number,
            }
            for stack in stacks_dtm
        ]

    @fail_quietly("Unable to create time map", return_value={})
    def _create_time_map(self, samples):
        """
        For the list of samples, createa dict of:

        second since attack start => attacks in that second.
        """
        time_map = {}

        for sample in samples:
            elapsed_secs = sample["timestamp"]["elapsed"]
            time_map.setdefault(elapsed_secs, 0)
            time_map[elapsed_secs] += 1

        return time_map

    def to_json(self):
        common_fields = {
            "startTime": 0,
            "total": 0,
        }
        json = {
            "startTime": self.start_time_ms,
            "blocked": common_fields,
            "exploited": common_fields,
            "ineffective": common_fields,
            "suspicious": common_fields,
        }

        RESPONSE_MAP = {
            AttackDtm.MONITORED: "exploited",
            AttackDtm.BLOCKED: "blocked",
            AttackDtm.PROBED: "ineffective",
            # Suspicious was not added to protobuf but needed for various rules
            6: "suspicious",
        }

        relevant_mode = RESPONSE_MAP.get(self.response)
        if relevant_mode is None:
            # Don't know what response is so just report default info so we can debug.
            return json

        samples = self._convert_samples()

        json[relevant_mode] = {
            "total": 1,  # always 1 until batching happens
            "startTime": self.start_time_ms,
            "attackTimeMap": self._create_time_map(samples),
            "samples": samples,
        }

        return json
