# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import base64

import requests.models
from requests import put, post

import contrast
from contrast.agent.disable_reaction import DisableReaction
from contrast.agent.settings import Settings
from contrast.api import dtm_pb2
from contrast.api.architecture_component import ArchitectureComponent
from contrast.api.attack import Attack
from contrast.utils.timer import now_ms
from contrast.utils.decorators import fail_loudly
from contrast.utils.object_utils import NOTIMPLEMENTED_MSG
from contrast.utils.service_util import sleep
from contrast.utils.string_utils import ensure_string
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

PYTHON = "Python"

EVENT_ACTION_LOOKUP = {
    0: "CREATION",
    1: "PROPAGATION",
    2: "TRIGGER",
    3: "TAG",
    4: "A2A",
    5: "A2P",
    6: "A2O",
    7: "A2R",
    8: "O2A",
    9: "O2P",
    10: "O2O",
    11: "O2R",
    12: "P2A",
    13: "P2P",
    14: "P2O",
    15: "P2R",
}
EVENT_TYPE_LOOKUP = {
    0: "METHOD",
    1: "PROPAGATION",
    2: "TAG",
}


SLEEP_TIME_SECS = 900


class BaseTsMessage:
    def __init__(self):
        self._sent_count = 0
        self.settings = Settings()

        self.base_url = f"{self.settings.api_url}/api/ng/"
        self.proxy = (
            self.settings.build_proxy_url() if self.settings.is_proxy_enabled else {}
        )

        self.server_name_b64 = _b64url_stripped(self.settings.get_server_name())
        self.server_path_b64 = _b64url_stripped(self.settings.get_server_path())
        self.server_type_b64 = _b64url_stripped(self.settings.get_server_type())
        auth_header = f"{self.settings.api_user_name}:{self.settings.api_service_key}"

        self.headers = {
            # the Authorization header must not have its padding stripped
            "Authorization": base64.urlsafe_b64encode(auth_header.encode()).decode(),
            "API-Key": self.settings.api_key,
            "Server-Name": self.server_name_b64,
            "Server-Path": self.server_path_b64,
            "Server-Type": self.server_type_b64,
            "X-Contrast-Agent": f"{PYTHON} {contrast.__version__}",
            "X-Contrast-Header-Encoding": "base64",
        }

        self.body = ""

    @property
    def class_name(self):
        return type(self).__name__.lstrip("_")

    @property
    def name(self) -> str:
        """
        Used for request audit filename
        """
        raise NotImplementedError(NOTIMPLEMENTED_MSG)

    @property
    def path(self) -> str:
        """
        URL path for teamserver; used for formatting as "/api/ng/{path}"
        """
        raise NotImplementedError(NOTIMPLEMENTED_MSG)

    @property
    def request_method(self) -> str:
        raise NotImplementedError(NOTIMPLEMENTED_MSG)

    @property
    def expected_response_codes(self):
        return [204]

    @property
    def sent_count(self):
        return self._sent_count

    def sent(self):
        self._sent_count += 1

    @fail_loudly("Failed to process TS response")
    def process_response(
        self, response: requests.models.Response, reporting_client
    ) -> None:
        raise NotImplementedError(NOTIMPLEMENTED_MSG)

    def process_response_code(self, response, reporting_client):
        """
        Return True if response code is expected response code
        """
        if not isinstance(response, requests.models.Response):
            return False

        logger.debug(
            "Received %s response code from Teamserver",
            response.status_code,
            direct_to_teamserver=1,
        )

        if response.status_code in (409, 410, 412, 502):
            # 409: app is archived, 502 app is locked in TS
            # 410: app is not registered. We could send App startup for for not we won't
            # 412: API key no longer valid. While spec may say to resend msg in 15mins,
            #  in reality the app server and agent should simply be restarted.
            DisableReaction.run(self.settings)
            return False

        if response.status_code in (401, 408):
            # 401: Access forbidden because credentials failed to authenticate.
            # 408: TS Could not create settings in time.

            if isinstance(self, (ServerStart, ApplicationStartup)):
                DisableReaction.run(self.settings)
                return False

            logger.debug(
                "Sleeping for 15 minutes",
                direct_to_teamserver=1,
            )

            sleep(SLEEP_TIME_SECS)

            reporting_client.retry_message(self)
            return False

        if response.status_code == 429:
            sleep_time = int(response.headers.get("Retry-After", SLEEP_TIME_SECS))

            logger.debug("Sleeping for %s seconds", sleep_time, direct_to_teamserver=1)

            sleep(sleep_time)

            reporting_client.retry_message(self)

        if response.status_code not in self.expected_response_codes:
            logger.debug(
                "Unexpected %s response from TS: %s",
                self.class_name,
                response.status_code,
                direct_to_teamserver=1,
            )
            return False

        return True


class BaseServerMsg(BaseTsMessage):
    @fail_loudly(f"Failed to process server settings response")
    def process_response(self, response, reporting_client):
        settings = Settings()
        if not self.process_response_code(response, reporting_client):
            return

        body = response.json()

        settings.apply_ts_server_settings(body)

        settings.process_ts_reactions(body)


class ServerActivity(BaseServerMsg):
    def __init__(self):
        super().__init__()

        self.body = {"lastUpdate": self.since_last_update}

    @property
    def name(self):
        return "activity_server"

    @property
    def path(self):
        return "activity/server"

    @property
    def request_method(self):
        return put

    @property
    def expected_response_codes(self):
        return [200, 304]

    @property
    def since_last_update(self):
        """
        Time in ms since server have been updated.
        If never updated, then it's been 0ms since then.
        """
        if self.settings.last_server_update_time_ms == 0:
            return 0
        return now_ms() - self.settings.last_server_update_time_ms

    @fail_loudly("Failed to process ServerActivity response")
    def process_response(self, response, reporting_client):
        settings = Settings()

        # TS will not send server settings unless lastUpdate is >= 5 mins (300_000 ms)
        # The response in those cases is 304.
        if (
            not self.process_response_code(response, reporting_client)
            or response.status_code == 304
        ):
            return

        body = response.json()

        settings.apply_ts_server_settings(body)

        settings.process_ts_reactions(body)


class ServerStart(BaseServerMsg):
    def __init__(self):
        super().__init__()

        self.body = {
            "environment": self.settings.config.get("server.environment"),
            "tags": self.settings.config.get("server.tags"),
            "version": contrast.__version__,
        }

    @property
    def name(self):
        return "agent_startup"

    @property
    def path(self):
        return "/servers/"

    @property
    def expected_response_codes(self):
        return [200]

    @property
    def request_method(self):
        return put


class BaseTsAppMessage(BaseTsMessage):
    def __init__(self):
        super().__init__()

        # App language should only be encoded for url paths, not for headers.
        self.app_language_b64 = _b64url_stripped(PYTHON)
        self.app_name_b64 = _b64url_stripped(self.settings.app_name)

        self.headers.update(
            {
                "Application-Language": PYTHON,
                "Application-Name": self.app_name_b64,
                "Application-Path": _b64url_stripped(self.settings.app_path),
            }
        )

    @property
    def since_last_update(self):
        """
        Time in ms since app settings have been updated.
        If never updated, then it's been 0ms since then.
        """
        if self.settings.last_app_update_time_ms == 0:
            return 0
        return now_ms() - self.settings.last_app_update_time_ms


class Preflight(BaseTsAppMessage):
    def __init__(self, activity):
        super().__init__()

        self.activity = activity

        self.body = {"messages": []}
        for idx, finding in enumerate(self.activity.findings):
            message = {
                "appLanguage": PYTHON,
                "appName": self.settings.app_name,
                "appPath": self.settings.app_path,
                "appVersion": self.settings.app_version,
                "code": "TRACE",
                "data": finding.preflight,
                "key": idx,
            }
            self.body["messages"].append(message)

    @property
    def name(self):
        return "preflight"

    @property
    def path(self):
        return "preflight"

    @property
    def request_method(self):
        return put

    @property
    def expected_response_codes(self):
        return [200]

    @fail_loudly("Failed to process Preflight response")
    def process_response(self, response, reporting_client):
        if not self.process_response_code(response, reporting_client):
            return

        body = response.text
        finding_idxs_to_report = self._parse_body(body)
        for finding_idx in finding_idxs_to_report:
            finding = self.activity.findings[finding_idx]
            traces_msg = _Traces(finding, self.activity.http_request)
            reporting_client.add_message(traces_msg)

    @staticmethod
    def _parse_body(body):
        """
        A preflight response body is a comma-separated list of finding indices that
        should be reported in a Traces message. Some elements of this list will have a
        *, meaning TS needs an AppCreate message before it will accept this finding. For
        now, we do not send findings with a *.

        TODO: PYT-2119 handle * preflight findings
        """
        indices = body.strip('"').split(",")
        return [int(index) for index in indices if index.isdigit()]


class _Traces(BaseTsAppMessage):
    def __init__(self, finding, request: dtm_pb2.HttpRequest):
        super().__init__()

        self.headers.update({"Report-Hash": finding.preflight.split(",")[-1]})
        self.body = self._build_body(finding, request)

    @property
    def name(self) -> str:
        return "traces"

    @property
    def path(self) -> str:
        return "traces"

    @property
    def request_method(self) -> str:
        return put

    @fail_loudly("Failed to process Traces response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)

    def _build_body(self, finding, request: dtm_pb2.HttpRequest):
        path, _, querystring = request.raw.partition("?")
        return {
            "created": (
                finding.events[-1].timestamp_ms if len(finding.events) > 0 else now_ms()
            ),
            "events": [
                {
                    "action": EVENT_ACTION_LOOKUP[event.action],
                    "args": [
                        {
                            # "hash": 0,  # not required
                            "tracked": arg.tracked,
                            "value": arg.value,
                        }
                        for arg in event.args
                    ],
                    # "code": "string",  # currently unused; maybe useful in the future
                    "eventSources": [
                        {
                            "sourceName": s.name,
                            "sourceType": s.type,
                        }
                        for s in event.event_sources
                    ],
                    "fieldName": event.field_name,
                    "object": {
                        # "hash": 0,  # not required
                        "tracked": event.object.tracked,
                        "value": event.object.value,
                    },
                    "objectId": event.object_id,
                    "parentObjectIds": [{"id": p.id} for p in event.parent_object_ids],
                    # properties not used for dataflow rules
                    # "properties": [{"key": "string", "value": "string"}],
                    "ret": {
                        # "hash": 0,  # not required
                        "tracked": event.ret.tracked,
                        "value": event.ret.value,
                    },
                    "signature": {
                        "argTypes": list(event.signature.arg_types),
                        "className": event.signature.class_name,
                        "constructor": event.signature.constructor,
                        # not required and we don't save this to the DTM
                        # "expressionType": "MEMBER_EXPRESSION",
                        # "flags": 0,  # java only
                        "methodName": event.signature.method_name,
                        # not required and we don't save this to the DTM
                        # "operator": "string",
                        "returnType": event.signature.return_type,
                        # "signature": "string",  # deprecated
                        "voidMethod": event.signature.void_method,
                    },
                    "source": event.source,
                    "stack": [
                        {
                            "eval": s.eval,
                            "file": s.file_name,
                            "lineNumber": s.line_number,
                            "method": s.method_name,
                            "signature": s.signature,
                            "type": s.type,
                        }
                        for s in event.stack
                    ],
                    # "tags": "string",  # we don't save this to the DTM
                    "taintRanges": [
                        {
                            "tag": t.tag,
                            "range": t.range,
                        }
                        for t in event.taint_ranges
                    ],
                    "target": event.target,
                    # "thread": "string",  # not required
                    "time": event.timestamp_ms,
                    "type": EVENT_TYPE_LOOKUP[event.type],
                }
                for event in finding.events
            ],
            # "evidence": "string",  # deprecated
            "properties": dict(finding.properties),
            "request": {
                "body": ensure_string(request.request_body_binary),
                # the WSGI environ supports only one value per request header. However
                # the server decides to handle multiple headers, we're guaranteed to
                # have only unique keys in request.request_headers (since we iterate
                # over webob's EnvironHeaders). Thus, each value list here is length-1.
                "headers": {k: [v] for k, v in request.request_headers.items()},
                "method": request.method,
                "parameters": {
                    h.key: list(h.values)
                    for h in request.normalized_request_params.values()
                },
                "port": request.receiver.port,
                "protocol": request.protocol,
                "queryString": querystring,
                "uri": path,
                "version": request.version,
            },
            "routes": [
                {
                    "count": r.count,
                    "observations": [{"url": r.url, "verb": r.verb}],
                    "signature": r.route,
                }
                for r in finding.routes
            ],
            "ruleId": finding.rule_id,
            "session_id": self.settings.config.session_id,
            "tags": finding.tags,
            "version": finding.version,
        }


class ObservedRoute(BaseTsAppMessage):
    def __init__(self, observed_route):
        # This message does not need "Application-Path" header but it doesn't hurt
        # either.
        super().__init__()
        self.base_url = f"{self.settings.api_url}/agents/v1.0/"

        self.body = {
            "signature": observed_route.signature,
            "verb": observed_route.verb,
            "url": observed_route.url,
            "sources": self._parse_sources(observed_route.sources),
        }

        session_id = self.settings.config.session_id
        if session_id:
            self.body.update({"session_id": session_id})

    @property
    def name(self):
        return "observed_route"

    @property
    def path(self):
        return (
            f"routes/{self.server_name_b64}/{self.server_path_b64}"
            f"/{self.server_type_b64}/{self.app_language_b64}/{self.app_name_b64}"
            "/observed"
        )

    @property
    def request_method(self):
        return post

    @fail_loudly("Failed to process ObservedRoute response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)

    def _parse_sources(self, sources):
        new_sources = []
        for source in sources:
            try:
                new_sources.append(dict(type=source.type, name=source.name))
            except Exception:
                logger.debug("Could not parse source %s", source)

        return new_sources


class ApplicationUpdate(BaseTsAppMessage):
    def __init__(self, libraries):
        super().__init__()

        self.headers.update({"Content-Type": "application/json"})

        # activity message sends "components" aka "architectures"
        # so we will not send the "components" field at this time.

        # field "timestamp" represents the amount of time that has passed
        # since the app settings were changed (not an actual timestamp).
        self.body = {
            "timestamp": self.since_last_update,
            "libraries": [
                lib.to_json(self.settings) for lib in libraries if lib.hash_code
            ],
        }

    @property
    def name(self):
        return "update_application"

    @property
    def path(self):
        return "update/application"

    @property
    def request_method(self):
        return put

    @fail_loudly("Failed to process ApplicationUpdate response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)


class ApplicationInventory(BaseTsAppMessage):
    def __init__(self, routes):
        # This message does not need "Application-Path" header but it doesn't hurt
        # either.
        super().__init__()
        self.base_url = f"{self.settings.api_url}/agents/v1.0/"

        self.body = {
            "routes": [route.to_json() for route in routes.values()],
        }

        session_id = self.settings.config.session_id
        if session_id:
            self.body.update({"session_id": session_id})

    @property
    def name(self):
        return "applications-inventory"

    @property
    def path(self):
        return "/".join(
            [
                "applications",
                self.server_name_b64,
                self.server_path_b64,
                self.server_type_b64,
                self.app_language_b64,
                self.app_name_b64,
                "inventory",
            ]
        )

    @property
    def request_method(self):
        return post

    @fail_loudly("Failed to process ApplicationInventory response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)


class ObservedLibraryUsage(BaseTsAppMessage):
    def __init__(self, observed_libraries):
        # This message does not need "Application-Path" header but it doesn't hurt
        # either.
        super().__init__()

        self.base_url = f"{self.settings.api_url}/agents/v1.0/"
        self.body = {"observations": []}

        for lib in observed_libraries:
            if len(lib.get("used_files")) > 0:
                message = {
                    "id": lib.get("hash_code"),
                    "names": list(lib.get("used_files")),
                }

                self.body["observations"].append(message)

    @property
    def name(self):
        return "applications-library-usage"

    @property
    def path(self):
        return "/".join(
            [
                "applications",
                self.server_name_b64,
                self.server_path_b64,
                self.server_type_b64,
                self.app_language_b64,
                self.app_name_b64,
                "library-usage",
            ]
        )

    @property
    def request_method(self):
        return post

    @fail_loudly("Failed to process ObservedLibraryUsage response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)


def _b64url_stripped(header_str):
    """
    For some headers, TS expects a value that
    - is base64 encoded using URL-safe characters
    - has any padding (= or ==) stripped

    This follows RFC-4648 - base64 with URL and filename safe alphabet
    """
    return base64.urlsafe_b64encode(header_str.encode()).rstrip(b"=").decode("utf-8")


class HeartBeat(BaseTsAppMessage):
    def __init__(self):

        super().__init__()
        self.base_url = f"{self.settings.api_url}/agents/v1.0/"

    @property
    def name(self):
        return "applications-heartbeat"

    @property
    def path(self):
        return "/".join(
            [
                "applications",
                self.server_name_b64,
                self.server_path_b64,
                self.server_type_b64,
                self.app_language_b64,
                self.app_name_b64,
                "heartbeat",
            ]
        )

    @property
    def request_method(self):
        return post

    @fail_loudly("Failed to process HeartBeat response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)


class ApplicationStartup(BaseTsAppMessage):
    def __init__(self):
        super().__init__()

        self.body = {
            "instrumentation": {
                "protect": {"enable": self.settings.is_protect_enabled()}
            }
        }

        if self.settings.config.get_session_metadata():
            self.body.update(
                {"session_metadata": self.settings.config.get_session_metadata()}
            )

        if self.settings.config.app_metadata:
            self.body.update({"metadata": self.settings.config.app_metadata})

        if self.settings.config.app_code:
            self.body.update({"code": self.settings.config.app_code})

        if self.settings.config.session_id:
            self.body.update({"session_id": self.settings.config.session_id})

        if self.settings.config.app_tags:
            self.body.update({"tags": self.settings.config.app_tags})

        if self.settings.config.app_group:
            self.body.update({"group": self.settings.config.app_group})

    @property
    def name(self):
        return "applications-create"

    @property
    def path(self):
        return "applications/create"

    @property
    def expected_response_codes(self):
        return [200]

    @property
    def request_method(self):
        return put

    @fail_loudly("Failed to process ApplicationStartup response")
    def process_response(self, response, reporting_client):
        if not self.process_response_code(response, reporting_client):
            return

        body = response.json()

        self.settings.apply_ts_app_settings(body)
        self.settings.process_ts_reactions(body)


class Activity(BaseTsAppMessage):
    def __init__(self, context):
        super().__init__()

        self.body = {"lastUpdate": self.since_last_update}

        self.body["inventory"] = {
            # Used by TeamServer to aggregate counts across a given time period, for Protect and attacker activity.
            "activityDuration": 0,
            "components": [],
        }
        if context.request.user_agent:
            self.body["inventory"]["browsers"] = [context.request.user_agent]
        if context.database_info:
            for db_info in context.database_info:
                arch_comp = ArchitectureComponent(db_info).to_json()
                self.body["inventory"]["components"].append(arch_comp)

        if context.attacks:
            self.body["defend"] = {"attackers": []}

            for attack_dtm in context.attacks:
                attack = Attack(attack_dtm, context.activity.http_request).to_json()
                self.body["defend"]["attackers"].append(
                    {
                        "protectionRules": {attack_dtm.rule_id: attack},
                        "source": {
                            "ip": context.request.client_addr or "",
                            "xForwardedFor": context.request.headers.get(
                                "X-Forwarded-For"
                            )
                            or "",
                        },
                    }
                )

    @property
    def name(self):
        return "activity-application"

    @property
    def path(self):
        return "activity/application"

    @property
    def request_method(self):
        return put

    @property
    def expected_response_codes(self):
        return [200, 204]

    @fail_loudly("Failed to process Activity response")
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)
