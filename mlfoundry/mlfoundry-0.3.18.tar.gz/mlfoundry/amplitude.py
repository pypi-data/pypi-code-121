import enum
import logging
import platform
import time
import typing
import uuid

import amplitude_tracker

try:
    from git.config import GitConfigParser
except Exception as ex:
    GitConfigParser = None

logger = logging.getLogger(__name__)

# API key for mlfoundry project
AMPLITUDE_API_KEY = "e4925dfc6d2831828b3e55ae83e19fd2"
NO_USER = "no_user"
EventPropertiesType = typing.Dict[str, str]
CHAR_LIMIT = 1024
__all__ = ["Event", "init", "track"]


@enum.unique
class Event(enum.Enum):
    GET_CLIENT = "GET_CLIENT"
    EXCEPTION = "EXCEPTION"
    #### Top level APIs
    GET_ALL_PROJECTS = "GET_ALL_PROJECTS"
    CREATE_RUN = "CREATE_RUN"
    GET_RUN = "GET_RUN"
    GET_ALL_RUNS = "GET_ALL_RUNS"
    ####
    #### Run Level APIs
    LOG_MODEL = "LOG_MODEL"
    LOG_DATASET = "LOG_DATASET"
    LOG_METRICS = "LOG_METRICS"
    LOG_PARAMS = "LOG_PARAMS"
    GET_DATASET = "GET_DATASET"
    GET_METRICS = "GET_METRICS"
    GET_PARAMS = "GET_PARAMS"
    GET_MODEL = "GET_MODEL"
    GET_TAGS = "GET_TAGS"
    SET_TAGS = "SET_TAGS"
    ####


class _AmplitudeClient:
    def __init__(self, api_key: str = AMPLITUDE_API_KEY) -> None:
        amplitude_tracker.write_key = api_key
        self.device_id = str(uuid.getnode())
        self.platform = platform.system()
        self.session_id = round(time.time() * 1000)
        try:
            # TODO:  pass email/user_id after we have integrated the login flow
            self.user_id = (
                GitConfigParser().get_value("user", "email", NO_USER)
                if GitConfigParser is not None
                else NO_USER
            )
        except Exception as ex:
            logger.warning(f"GitConfigParser raised {ex}")
            self.user_id = NO_USER
        try:
            self.user_properties = {
                "python_version": platform.python_version(),
                # Ideally this should not be in user_properties
                # the amplitude_tracker overwrites the top level platform key
                # https://github.com/RandomCoffee/amplitude-python/blob/b833ffeeefa18eb69d2f2378ec6e13eb2587cdfa/amplitude_tracker/client.py#L93
                "platform": self.platform,
                "platform_info": platform.platform(terse=True),
            }
        except Exception as ex:
            logger.warning(f"failed to get user properties {ex}")
            self.user_properties = {}

    def track(
        self,
        event: Event,
        event_properties: typing.Optional[EventPropertiesType] = None,
    ):
        event_properties = event_properties if event_properties is not None else {}
        try:
            for key in event_properties:
                event_properties[key] = str(event_properties[key])[:CHAR_LIMIT]
            amplitude_tracker.track(
                user_id=self.user_id,
                device_id=self.device_id,
                session_id=self.session_id,
                event_type=event.value,
                event_properties=event_properties,
                user_properties=self.user_properties,
            )
        except Exception as ex:
            logger.warning(f"failed to track event, {ex}")


class _FakeClient(_AmplitudeClient):
    def __init__(self, *args, **kwargs):
        ...

    def track(self, *args, **kwargs):
        ...


_amplitude_client: typing.Optional[_AmplitudeClient] = None


def init(disable_analytics: bool = False):
    global _amplitude_client
    if _amplitude_client is not None:
        logger.debug("amplitude already initialized")
        return
    if disable_analytics:
        logger.info("analytics is disabled")
        _amplitude_client = _FakeClient()
    else:
        _amplitude_client = _AmplitudeClient()


def track(
    event: Event,
    event_properties: typing.Optional[EventPropertiesType] = None,
):
    if _amplitude_client is None:
        init()
    _amplitude_client.track(event=event, event_properties=event_properties)
