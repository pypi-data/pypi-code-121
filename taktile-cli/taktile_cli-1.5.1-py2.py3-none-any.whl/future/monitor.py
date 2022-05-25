import logging
import time
import typing as t
from functools import singledispatch, wraps
from operator import attrgetter

import pandas as pd  # type: ignore
import pydantic
import requests
from fastapi import Request
from taktile_types.enums.monitor import MonitorSourceType, MonitorType
from taktile_types.schemas.monitor import MonitorDataV2, MonitoringPayload

from tktl.core.exceptions import EndpointInstantiationError
from tktl.future.registration.endpoints.abc import EndpointResponse, XType, YType

from .settings import settings

logger = logging.getLogger(__name__)


class Tracker:
    """Tracker."""

    def __init__(self, request: Request, endpoint_name: str):
        """__init__.

        Parameters
        ----------
        request : Request
            request object of the current request life cycle
        endpoint_name : str
            endpoint's name
        """
        self._values: t.List[MonitorDataV2] = []
        self._request: Request = request
        self._endpoint_name = endpoint_name

    def log_categorical(
        self,
        key: str,
        value: t.Union[int, float, None, t.Sequence[t.Union[int, float, None]]],
        source_type: MonitorSourceType = MonitorSourceType.CUSTOM,
    ):
        """log_categorical logs a categorical value. The differentiation
        between numerical and categorical is important when binning the data.

        Parameters
        ----------
        name : str
            key of the datim
        value : t.Union[int, float, None, t.Sequence[t.Union[int, float, None]]]
            value(s) of the datum
        """
        if not isinstance(value, list):
            value = [value]  # type: ignore

        self._values.append(
            MonitorDataV2(
                value=value,
                type=MonitorType.CATEGORY,
                name=key,
                source_type=source_type,
            )
        )

    def log_numerical(
        self,
        key: str,
        value: t.Union[int, float, None, t.Sequence[t.Union[int, float, None]]],
        source_type: MonitorSourceType = MonitorSourceType.CUSTOM,
    ):
        """log_numerical logs a numerical value. The differentiation between
        numerical and categorical is important when binning the data.

        Parameters
        ----------
        key : str
            key of the datum
        value : t.Union[int, float, None, t.Sequence[t.Union[int, float, None]]]
            value(s) of the datum
        """
        if not isinstance(value, list):
            value = [value]  # type: ignore

        self._values.append(
            MonitorDataV2(
                value=value, type=MonitorType.NUMERIC, name=key, source_type=source_type
            )
        )

    def finalize_payload(self) -> t.Optional[MonitoringPayload]:
        """finalize_payload finalizes the payload to be sent across the wire.

        Returns
        -------
        t.Optional[MonitoringPayload]

        The return is None if no data has been added during this request life
        cycle.
        """
        if not self._values:
            return None

        return MonitoringPayload(
            version=2,
            git_sha=settings.TAKTILE_GIT_SHA,
            git_ref=settings.TAKTILE_GIT_REF,
            repository_id=settings.REPOSITORY_ID,
            endpoint=self._endpoint_name,
            user_agent=self._request.headers.get("user-agent"),
            timestamp=int(time.time() * 1000),
            data=self._values,
        )


def tracker_inject(
    request: Request,
    endpoint_name: str,
    track_inputs: t.Optional[t.List[str]] = None,
    track_outputs: t.Optional[t.List[str]] = None,
):
    """Use tracker_inject to inject a Tracker into a function and
    handle data tracking of inputs and outputs.

    Example
    -------

    @create_tracker_inject_wrapper(request)
    def f(x: int, t: Tracker) -> float:
        ...

    is a function f(x: int) -> float


    Parameters
    ----------
    request : Request
        request of the current request life cycle
    endpoint_name : str
        endpoint's name
    track_inputs : t.Optional[t.List[str]]
        input keys to be tracked
    track_outputs : t.Optional[t.List[str]]
        output keys to be tracked
    """

    def inject_tracker_wrapper(func):

        type_hints = t.get_type_hints(func)
        tracker_kwarg = [
            a for (a, b) in type_hints.items() if a != "return" and b == Tracker
        ]

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not tracker_kwarg and track_inputs is None and track_outputs is None:
                # Do this in the beginning to reduce impact on untracked functions
                return func(*args, **kwargs)

            tracker = Tracker(request, endpoint_name)

            if tracker_kwarg:
                kwargs[tracker_kwarg[0]] = tracker
            _track_values(args[0], track_inputs, tracker, MonitorSourceType.INPUT)
            result = func(*args, **kwargs)

            if isinstance(result, EndpointResponse):
                _track_values(
                    result.return_value,
                    track_outputs,
                    tracker,
                    MonitorSourceType.OUTPUT,
                )

            else:
                _track_values(result, track_outputs, tracker, MonitorSourceType.OUTPUT)

            payload = tracker.finalize_payload()

            if payload is None:
                return result

            if isinstance(result, EndpointResponse):
                result.tasks.append(lambda: _send_payload(payload))
                return result

            else:
                return EndpointResponse(
                    return_value=result, tasks=[lambda: _send_payload(payload)]
                )

        return wrapper

    return inject_tracker_wrapper


def _send_payload(payload: MonitoringPayload):
    if settings.TKTL_MONITORING_ENDPOINT is not None:
        requests.post(
            settings.TKTL_MONITORING_ENDPOINT,
            data=payload.json(),
            headers={"Content-Type": "application/json"},
            timeout=3,
        )
    else:
        print(payload.json())  # noqa


def _pandas_dtype_to_monitor_type(t: pd.Series.dtype) -> MonitorType:
    if t.dtype.kind in ["i", "f"]:
        return MonitorType.NUMERIC
    return MonitorType.CATEGORY


def _track_values(
    value: t.Union[XType, YType],
    keys: t.Optional[t.List[str]],
    tracker: Tracker,
    source_type: MonitorSourceType,
) -> None:
    if keys is None:
        return

    for key in keys:
        tracking_data = extract_monitor_element(value, key=key)
        if tracking_data is not None:

            if tracking_data[1] == MonitorType.CATEGORY:
                tracker.log_categorical(key, tracking_data[0], source_type)  # type: ignore
            elif tracking_data[1] == MonitorType.NUMERIC:
                tracker.log_numerical(key, tracking_data[0], source_type)  # type: ignore


@singledispatch
def extract_monitor_element(
    value: t.Union[XType, YType], *, key: str
) -> t.Optional[t.Tuple[t.Sequence[t.Union[str, float, int]], MonitorType]]:
    return None


@extract_monitor_element.register
def _extract_df(
    value: pd.DataFrame, key: str
) -> t.Optional[t.Tuple[t.Sequence[t.Union[str, float, int]], MonitorType]]:
    column = value[key]
    return extract_monitor_element(column, key)


@extract_monitor_element.register
def _extract_series(
    value: pd.Series, key: str
) -> t.Optional[t.Tuple[t.Sequence[t.Union[str, float, int]], MonitorType]]:
    try:
        type_ = _pandas_dtype_to_monitor_type(value)
        python_list = value.tolist()

        if python_list:
            if value.dtype.kind == "M":
                python_list = [
                    int(x.timestamp()) if not pd.isnull(x) else None
                    for x in python_list
                ]
            python_list = [x if not pd.isnull(x) else None for x in python_list]
            return python_list, type_

        return None
    except KeyError as exc:
        logger.warning("KeyError while extracting value from series: %s", str(exc))
        return None


PYDANTIC_TYPE_TRANSLATION = {
    "integer": MonitorType.NUMERIC,
    "boolean": MonitorType.CATEGORY,
    "number": MonitorType.NUMERIC,
    "string": MonitorType.CATEGORY,
}


def _fetch_reference(schema: t.Dict[str, t.Any], reference: str):
    """
    Follow json references. Pydantic creates these in the form
    `{'$ref': '#/definitions/ReferencedModel'}` and adds all
    referenced definitions at the schema's top level, e.g.
    {
      'definitions': {
        'ReferencedModel':{
          'description': 'An enumeration.',
          'enum': ['a', 'b', 'c'],
          'title': 'ReferencedModel',
          'type': 'string'
        }
      }
    }
    """
    key, _, rest = reference.partition("/")
    if key == "#":  # special top-level key - ignore
        return _fetch_reference(schema, rest)
    if rest:
        return _fetch_reference(schema[key], rest)
    return schema[key]


@extract_monitor_element.register
def _extract_pydantic(
    value: pydantic.BaseModel, key: str
) -> t.Optional[t.Tuple[t.Sequence[t.Union[str, float, int]], MonitorType]]:

    parent_key, _, child_key = key.rpartition(".")

    try:
        parent = value if not parent_key else attrgetter(parent_key)(value)
        item = getattr(parent, child_key)

        child_schema = parent.schema()["properties"][child_key]
        # resolve reference types
        # these are saved under 'definitions' in the top level schema
        # See https://pydantic-docs.helpmanual.io/usage/schema/ for details
        if "$ref" in child_schema:
            child_schema = _fetch_reference(value.schema(), child_schema["$ref"])

        if "enum" in child_schema:
            # depending on whether the pydantic attribute `use_enum_values`
            # is set, we'll get either an enum or its value here
            return ([getattr(item, "value", item)], MonitorType.CATEGORY)

        type_ = PYDANTIC_TYPE_TRANSLATION[child_schema["type"]]
        return ([item], type_)

    except (KeyError, AttributeError) as exc:
        logger.warning("KeyError while extracting pydantic value: %s", str(exc))
        return None


def verify_tracking_config(value: t.Union[XType, YType], keys: t.List[str]):
    if isinstance(value, pd.Series):
        if len(keys) >= 2:
            raise EndpointInstantiationError(
                "Trying to track multiple values of a series"
            )
    if isinstance(value, pd.DataFrame):
        tracked = set(keys)
        given = set(value.columns.tolist())
        if not tracked.issubset(given):
            raise EndpointInstantiationError(
                f"Couldn't find the following tracking keys: {tracked.difference(given)}"
            )
