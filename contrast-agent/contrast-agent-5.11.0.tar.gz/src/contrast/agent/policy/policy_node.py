# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy import constants
from contrast.agent.assess.assess_exceptions import ContrastAssessException
from contrast.agent.policy.constants import ALL_ARGS, OBJECT, RETURN
from contrast.api.dtm_pb2 import TraceEvent


UNDERSCORE = "_"
COMMA = ","
COLON = ":"


class PolicyNode(object):
    def __init__(
        self,
        module="",
        class_name="",
        instance_method=True,
        method_name="",
        source="",
        target="",
        tags=None,
        policy_patch=True,
    ):
        self.module = module
        self.class_name = class_name

        # If no class_name is given, it indicates that this node corresponds to a
        # standalone function, not a method. This means that instance_method is always
        # False. Otherwise we use the given value of instance_method. However, the
        # default for this argument will be True if not given for all policy nodes,
        # which means that only methods that are **not** instance methods must provide
        # it explicitly. This value is used to determine whether or not the first
        # positional argument should be treated as "self" or not by our policy
        # machinery
        self.instance_method = instance_method if class_name else False

        self.method_name = method_name

        self.sources = self.parse_source_or_target(source)
        self.targets = self.parse_source_or_target(target)

        self.ts_valid_source = self.ts_represent(source)
        self.ts_valid_target = self.ts_represent(target)

        self.tags = set()

        if tags:
            self.tags.update(tags)

        # This attribute indicates whether a given policy node corresponds to a patch
        # that should be applied by policy. It defaults to True. However, many of our
        # policy nodes are **not** patched by policy but instead are patched in a
        # different way. For example, nearly all of our string propagators are applied
        # as C hooks. In these cases we still use the policy node for reporting
        # purposes, but we don't want a policy patch.
        self.policy_patch = policy_patch

        self.skip_stacktrace = False
        self.properties = {}

    @property
    def name(self):
        """
        Fully specified unique name for this node

        Includes module name, class name (if applicable) and method name
        """
        return f"{self.location}.{self.method_name}"

    @property
    def location(self):
        """
        Property indicating the fully specified location of the patched method/function

        For a method of a class:
            <module_path>.<class_name>.<method_name>

        For a function:
            <module_path>.<function_name>
        """
        return f"{self.module}{'.' + self.class_name if self.class_name else ''}"

    def add_property(self, name, value):
        if not name or not value:
            return

        self.properties[name] = value

    @property
    def node_class(self):
        return self.__class__.__name__.replace("Node", "")

    @property
    def node_type(self):
        return "TYPE_METHOD"

    @property
    def version_mismatch(self):
        """
        Indicates whether this node is incompatible with the current Python version

        Previously the finest granularity we have is Py2.7 vs Py3, but eventually we may
        update it to have more specific version specifications.
        """
        pass

    def parse_source_or_target(self, str_rep):
        """
        Given a string source or target, split it into its list representation
        by splitting on ',' and appending the appropriate represntation to the list.

        :param str_rep: string representation of a source or target, such as 'ARG_0, OBJ'
        :return: list representation of source or target, [0, 'OBJ']
        """
        ret = []

        if not str_rep:
            return []

        for item in str_rep.split(COMMA):
            if item == constants.OBJECT:
                ret.append(item)

            elif item == constants.RETURN:
                ret.append(item)

            elif item == constants.ALL_ARGS:
                ret.append(item)

            elif item == constants.ALL_KWARGS:
                ret.append(item)

            # handle ARG_#
            elif item.startswith(constants.ARG + UNDERSCORE):
                arg_num = item.split(UNDERSCORE)[1]
                ret.append(int(arg_num))

            # handle KWARG:name
            elif item.startswith(constants.KWARG + COLON):
                kwarg_name = item.split(COLON)[1]
                ret.append(kwarg_name)

            else:
                return []

        return ret

    def ts_represent(self, str_rep):
        """
        Convert source/target from policy.json into TS-valid version.
        * ARG_# --> P#
        * ARG_0,KWARG:location --> P0,KWARG:location
            TS will ignore everything after P0; kwargs are not directly supported in TS
        * KWARG:location --> P0
            Pure kwarg functions are rare in Python but we must support them. However,
            kwargs are not directly supported in TS so for now we send a fake P0.
        * ALL_ARGS or ALL_KWARGS --> P0
            TS does not currently support sending an arbitrary number of args/kwargs for
            source/target value
        """
        if not str_rep:
            return ""
        if str_rep.startswith(
            (
                constants.KWARG,
                constants.ALL_ARGS,
                constants.ALL_KWARGS,
            )
        ):
            return "P0"

        return str_rep.replace("ARG_", "P")

    def get_matching_first_target(self, self_obj, ret, args, kwargs):
        node_target = self.targets[0]

        if node_target is None:
            return None

        if node_target == ALL_ARGS:
            return args

        if node_target == RETURN:
            return ret

        if node_target == OBJECT:
            return self_obj

        if args and isinstance(node_target, int):
            return args[node_target]

        return kwargs.get(node_target) if kwargs else None

    def validate(self):
        if not self.module:
            raise ContrastAssessException(
                f"{self.node_class} unknown did not have a proper module. Unable to create."
            )

        if not self.method_name:
            raise ContrastAssessException(
                f"{self.node_class} did not have a proper method name. Unable to create."
            )

        self.validate_tags()

    def validate_tags(self):
        if not self.tags:
            return

        for item in self.tags:
            if not (
                item in constants.VALID_TAGS or item in constants.VALID_SOURCE_TAGS
            ):
                raise ContrastAssessException(
                    f"{self.node_class} {self.name} had an invalid tag. {item} is not a known value."
                )

    def _type_to_action(self, sources_or_targets):
        """
        Convert a list of sources or targets into a TS-valid action string.
        """
        if not sources_or_targets:
            return ""

        if len(sources_or_targets) > 1:
            return constants.ALL_TYPE

        item = sources_or_targets[0]

        if item in (constants.ALL_ARGS, constants.ALL_KWARGS):
            return constants.ALL_TYPE

        if item == constants.OBJECT:
            return constants.OBJECT_KEY

        # only target, not source, can be return type
        if item == constants.RETURN:
            return constants.RETURN_KEY

        return constants.ARG_OR_KWARG

    def build_action(self):
        """
        Convert our action, built from our source and target, into
        the TS appropriate action.

        Creation (source nodes) don't have sources (they are the source)
        Trigger (trigger nodes) don't have targets (they are the target)
        Everything else (propagation nodes) are Source2Target
        :return: self.event_action
        """
        if not self.sources:
            event_action = TraceEvent.Action.Value(constants.CREATION_TYPE)
        elif not self.targets:
            event_action = TraceEvent.Action.Value(constants.TRIGGER_TYPE)
        else:
            source = self._type_to_action(self.sources)
            target = self._type_to_action(self.targets)
            str_action = source + constants.TO_MARKER + target

            event_action = TraceEvent.Action.Value(str_action)

        return event_action

    def __repr__(self):
        return f"{self.__class__.__name__} - {self.name}"
