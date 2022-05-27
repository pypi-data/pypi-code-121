# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import threading

from contrast.agent.policy.constants import (
    ALL_ARGS,
    ALL_KWARGS,
    OBJECT,
    RETURN,
    TRIGGER_TYPE,
    CREATION_TYPE,
)

from contrast.agent.assess.truncate import truncate, truncate_tainted_string
from contrast.agent.assess.utils import get_properties
from contrast.agent.settings import Settings
from contrast.api.dtm_pb2 import (
    ParentObjectId,
    TraceEvent,
    TraceEventObject,
    TraceEventSource,
)
from contrast.utils.base64_utils import base64_encode
from contrast.utils.decorators import log_time
from contrast.utils.object_utils import safe_copy
from contrast.utils.stack_trace_utils import (
    build_stack,
    clean_stack,
    convert_stack_frame_element,
)
from contrast.utils.string_utils import protobuf_safe, ensure_string
from contrast.utils.timer import now_ms
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

INIT = "__init__"
INITIALIZERS = (INIT, "__new__")
NONE_STRING = str(None)
TRACE_EVENT_TYPE_MAP = {"METHOD": 0, "PROPAGATOR": 1, "TAGGER": 2, "TAG": 2}


class _TriggerTimeMixin(object):
    """
    Contrast Event methods only called on all ContrastEvent instances
    if a trigger is reached.
    """

    def to_dtm(self):
        """
        Convert a ContrastEvent to a TraceEvent.
        """
        self._update_init_return()

        event = TraceEvent()

        event.type = TRACE_EVENT_TYPE_MAP.get(self.node.node_type, 1)
        event.action = self.event_action
        event.timestamp_ms = self.time
        event.thread = str(self.thread)

        self._build_all_event_objects(event)

        stack = clean_stack(self._raw_stack, depth=20, for_trace=True)
        for frame in stack:
            convert_stack_frame_element(frame, event)

        safe_source_name = protobuf_safe(self.source_name)
        event.field_name = safe_source_name

        if self.source_type:
            event.event_sources.extend([self.build_source_event(safe_source_name)])

        event.object_id = int(self.event_id)

        if self.parent_ids:
            for parent_id in self.parent_ids:
                parent = ParentObjectId()
                parent.id = parent_id
                event.parent_object_ids.extend([parent])

        self._build_complete_signature(event)
        self._validate_event(event)

        return event

    def _update_init_return(self):
        """
        For purposes of pretty reporting in Teamserver, we will say the
        `__init__` instance method return the `self` object (the object getting
        instantiated) instead of `None`, even though `None` is the return value of
        `__init__` methods.

        This will not apply if the node is not a class (it's possible someone
        creates a module level function called `__init__` or if the return
        value is already populated (for safety).
        """
        if self.node.method_name == INIT and self.node.class_name is not None:
            self.ret = self.ret or self.obj

    def build_source_event(self, safe_source_name):
        """
        Create a new TraceEventSource

        :param safe_source_name: source name or empty string
        :return: TraceEvenSource
        """
        trace_event_source = TraceEventSource()

        trace_event_source.type = self.source_type
        trace_event_source.name = safe_source_name

        return trace_event_source

    def _set_event_source_and_target(self, event):
        """
        We have to do a little work to figure out what our TS appropriate
        target is. To break this down, the logic is as follows:
        1) If my node has a target, work on targets. Else, work on sources.
           Per TS law, each node must have at least a source or a target.
           The only type of node w/o targets is a Trigger, but that may
           change.
        2) I'll set the event's source and target to TS values.
        """
        if self.node.targets:
            event.source = self.node.ts_valid_source
            event.target = self.node.ts_valid_target
        elif self.node.sources:
            event.source = self.node.ts_valid_target or self.node.ts_valid_source

    def _build_all_event_objects(self, event):
        """
        First populate event.source and event.target
        Then populate fields of event.object, event.ret, and event.args (contains both
        args and kwargs for python) which are each `TraceEventObject`s
        """
        self._set_event_source_and_target(event)

        self._build_event_object(
            event, event.object, self.obj, self.taint_location == OBJECT
        )
        self._build_event_object(
            event, event.ret, self.ret, self.taint_location == RETURN
        )

        for index, arg in enumerate(self.args):
            event_obj = TraceEventObject()
            self._build_event_object(
                event, event_obj, arg, self.taint_location == index
            )
            event.args.append(event_obj)

        if not self.kwargs:
            return

        event_obj = TraceEventObject()
        is_kwargs_taint_target = self.taint_location is ALL_KWARGS or isinstance(
            self.taint_location, str
        )
        self._build_event_object(event, event_obj, self.kwargs, is_kwargs_taint_target)
        event.args.append(event_obj)

    def _build_event_object(self, event, event_obj, obj, is_taint_target):
        str_representation, splat = _obj_to_str(obj)

        splat_len = None
        if splat:
            splat_len = len(str_representation)

        if is_taint_target:
            self._add_taint_ranges(event, event_obj, obj, splat_len)
            str_representation = truncate_tainted_string(str_representation, event)
        else:
            str_representation = truncate(str_representation)

        event_obj.value = base64_encode(str_representation)

    def _add_taint_ranges(self, event, event_obj, target, splat_len):
        """
        Populate event.taint_ranges
        """
        if self.taint_location is None:
            return

        if isinstance(target, dict):
            if self.taint_location == ALL_KWARGS and self.possible_key:
                properties = get_properties(target.get(self.possible_key, None))
            else:
                properties = get_properties(target.get(self.taint_location, None))
        else:
            properties = get_properties(target)

        if properties is None:
            return

        if splat_len is not None:
            tag_ranges = properties.tags_to_dtm(splat_range=(0, splat_len))
        else:
            tag_ranges = properties.tags_to_dtm()

        event.taint_ranges.extend(tag_ranges)
        # For now, only the taint_target needs to be officially marked as tracked.
        # This means that agent-tagged strings may not be marked as "tracked" for SR.
        # This may change in the future if we change the corresponding TS endpoint; in
        # that case, use recursive_is_tracked for each TraceEventObject.
        event_obj.tracked = True

    def _build_complete_signature(self, event):
        return_type = type(self.ret).__name__ if self.ret is not None else NONE_STRING

        event.signature.return_type = return_type
        # We don't want to report "BUILTIN" as a module name in Team Server
        event.signature.class_name = self.node.location.replace("BUILTIN.", "")
        event.signature.method_name = self.node.method_name

        if self.args:
            for item in self.args:
                arg_type = type(item).__name__ if item else NONE_STRING
                event.signature.arg_types.append(arg_type)

        if self.kwargs:
            arg_type = type(self.kwargs).__name__
            event.signature.arg_types.append(arg_type)

        event.signature.constructor = self.node.method_name in INITIALIZERS

        # python always returns None if not returned
        event.signature.void_method = False

        if not self.node.instance_method:
            event.signature.flags = 8

    def _validate_event(self, event):
        """
        TS is not able to render a vulnerability correctly if the source string index 0
        of the trigger event, ie event.source, is not a known one.

        See TS repo DataFlowSnippetBuilderVersion1.java:buildMarkup

        :param event: TraceEvent
        :return: None
        """
        allowed_trigger_sources = ["O", "P", "R"]
        if (
            event.action == TraceEvent.Action.Value(TRIGGER_TYPE)
            and event.source[0] not in allowed_trigger_sources
        ):
            # If this is logged, check the node in policy.json corresponding to
            # this event and how the agent has transformed the source string
            logger.debug("WARNING: trigger event TS-invalid source %s", event.source)


class ContrastEvent(_TriggerTimeMixin):
    """
    This class holds the data about an event in the application
    We'll use it to build an event that TeamServer can consume if
    the object to which this event belongs ends in a trigger.
    """

    ATOMIC_ID = 0

    @log_time("initializing ContrastEvent")
    def __init__(
        self,
        node,
        tagged,
        self_obj,
        ret,
        args,
        kwargs,
        parent_ids,
        possible_key,
        source_type=None,
        source_name=None,
    ):
        self.node = node
        self.tagged = tagged
        self.source_type = source_type
        self.source_name = source_name
        self.parent_ids = parent_ids
        self.possible_key = possible_key
        self.obj = self_obj
        self.ret = ret
        self.args = safe_copy(args)
        self.kwargs = safe_copy(kwargs)

        # These are needed only at trigger-time but values must be set at init.
        self.time = now_ms()
        self.thread = threading.current_thread().ident
        self.event_id = ContrastEvent._atomic_id()

        self.event_action = self.node.build_action()

        self._raw_stack = build_stack() if self._should_get_stack else []

        # This must happen at init for stream events to work.
        self.taint_location = None
        self._update_method_information()

    @property
    def _should_get_stack(self):
        """
        Determine if event.stack should be populated or not.

        Get stacktrace for the event EXCEPT if
          1. the node explicitly indicates not to collect a stacktrace, which is the
                case for WSGI environ sources
          2. assess.stacktraces is configured to NONE
          3. assess.stacktraces is configured to SOME and event action is not
                creation or trigger


        :return: bool if to get stacktrace
        """
        settings = Settings()

        reportable_actions = (
            TraceEvent.Action.Value(CREATION_TYPE),
            TraceEvent.Action.Value(TRIGGER_TYPE),
        )

        if (
            self.node.skip_stacktrace
            or settings.is_collect_stacktraces_none()
            or (
                settings.is_collect_stacktraces_some()
                and self.event_action not in reportable_actions
            )
        ):
            return False

        return True

    @classmethod
    def _atomic_id(cls):
        ret = cls.ATOMIC_ID
        cls.ATOMIC_ID += 1
        return ret

    def _update_method_information(self):
        """
        For nicer reporting, we lie about the tagged value. For example, a call to
        split() returns a list of strings: ["foo", "bar"]. In the properties for "foo",
        the split event shows a return value of only "foo" instead of the whole list.
        """
        self.taint_location = self._find_taint_location()

        if self.taint_location is None:
            # This would be for trigger nodes without source or target. Trigger rule was
            # violated simply by a method being called. We'll save all the information,
            # but nothing will be marked up, as nothing need be tracked.
            return

        if self.taint_location == OBJECT:
            self.obj = self.tagged
            return

        if self.taint_location == RETURN:
            self.ret = self.tagged

    def _find_taint_location(self):
        """
        Based on what we know about the call that caused this event's creation,
        determine the appropriate taint location. Fall back to returning the
        first element in candidate_taint_locations. This method is greedy, so it
        will return the first valid taint location based on the order of candidate
        locations provided.

        Example:

        args = ("irrelevant string",)
        kwargs = {"irrelevant_key": "irrelevant_value", "important_key": "user_input"}
        candidate_taint_locations = [1, 2, "important_key"]

        In this case, we return "important_key" since there is no ARG_1 or ARG_2.

        @return: The appropriate element of candidate_taint_locations, or the first
            element if no suitable matches are found, or None if the list is empty.
        """
        candidate_taint_locations = self.node.targets or self.node.sources

        if not candidate_taint_locations:
            return None

        for candidate_location in candidate_taint_locations:
            found = (
                (candidate_location == RETURN)
                or (candidate_location == OBJECT and self.obj is not None)
                or (candidate_location == ALL_ARGS and self.args)
                or (candidate_location == ALL_KWARGS and self.kwargs)
                or (
                    isinstance(candidate_location, int)
                    and candidate_location < len(self.args)
                )
                or (
                    isinstance(candidate_location, str)
                    and candidate_location in self.kwargs
                )
            )
            # pylint doesn't like this in an if statement, but an assignment is ok
            if found:
                return candidate_location

        logger.debug(
            "WARNING: unable to find event taint location: %s %s %s %s %s",
            self.obj,
            self.ret,
            self.args,
            self.kwargs,
            candidate_taint_locations,
        )
        return candidate_taint_locations[0]


def _obj_to_str(self_obj):
    """
    Attempt to get a string representation of an object

    Right now we do our best to decode the object, but we handle any
    decoding errors by replacing with �. This technically is a loss
    of information when presented in TS, but it allows us to preserve
    the taint range information, which arguably is more important for
    Assess. In the future we might want to implement more robust
    handling of non-decodable binary data (i.e. to display escaped
    data with an updated taint range).

    If the object isn't stringy, then just return the string
    representation. In this case, we will need to splat the displayed
    taint range since we're not able to map tag ranges.

    :param self_obj: any python object, str, byte, bytearray, etc
    :return:
        1. str representing the object
        2. whether to splat the taint ranges or not, depending on if we can stringify
           the obj successfully
    """
    splat = False

    try:
        if isinstance(self_obj, bytearray):
            str_representation = self_obj.decode(errors="replace")
        else:
            str_representation = ensure_string(self_obj, errors="replace")
        if len(str_representation) != len(self_obj):
            # tag ranges won't line up properly if the length of the string
            # representation differs from the original length
            splat = True
    except Exception:
        str_representation = str(self_obj)
        splat = True

    return str_representation, splat
