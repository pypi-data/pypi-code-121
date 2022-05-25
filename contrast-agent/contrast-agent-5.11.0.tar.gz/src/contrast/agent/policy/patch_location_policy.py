# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.deadzone_node import DeadZoneNode
from contrast.agent.assess.policy.propagation_node import PropagationNode
from contrast.agent.assess.policy.source_node import SourceNode
from contrast.agent.assess.policy import propagation_policy
from contrast.agent.assess.policy import source_policy
from contrast.agent.assess.policy import trigger_policy
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.settings import Settings
from contrast.utils.decorators import cached_property


class PatchLocationPolicy(object):
    """
    Container for all policy nodes that pertain to a single patch location

    A patch location is a specific function or method that we patch. A single patch
    location may correspond to multiple policy nodes. Since import hooks are applied at
    the module level, there is a one-to-many relationship between each module and the
    corresponding PatchLocationPolicy instances.
    """

    def __init__(self, node):
        self.module = node.module
        self.class_name = node.class_name
        self.method_name = node.method_name
        # This is a copy of the name attribute of each PolicyNode represented by this
        # PatchLocationPolicy instances. All policy nodes represented by this location
        # must have the same name.
        self.name = node.name

        self.deadzone_nodes = []
        self.source_nodes = []
        self.propagator_nodes = []
        self.trigger_nodes = []
        self.patch_locations = []
        self.analysis_func = None

    def add_node(self, node):
        """
        Add a policy node for this patch location
        """
        # This is a sanity check to ensure that we don't accidentally add a node that
        # corresponds to a different patch location.
        assert node.name == self.name

        if isinstance(node, DeadZoneNode):
            self.deadzone_nodes.append(node)
        elif isinstance(node, PropagationNode):
            self.propagator_nodes.append(node)
        elif isinstance(node, SourceNode):
            self.source_nodes.append(node)
        elif isinstance(node, TriggerNode):
            self.trigger_nodes.append(node)

    def assign_analysis_func(self):
        """
        Store the analysis function as an optimization.
        This should only be called when we know there is only one node for this
        patch location and for assess only.
        """
        node = self.all_nodes[0]

        if isinstance(node, TriggerNode):
            self.analysis_func = trigger_policy.apply
        elif isinstance(node, PropagationNode):
            self.analysis_func = propagation_policy.apply
        elif isinstance(node, SourceNode):
            self.analysis_func = source_policy.apply

    @property
    def has_patches(self):
        """
        Indicates whether any nodes at this location require policy patches
        """
        return any([node.policy_patch for node in self.all_nodes])

    @property
    def is_deadzone(self):
        """
        Indicates if there are any deadzone nodes.

        NOTE: at this time, deadzone nodes and any other nodes are mutually exclusive.
        That is, all patches will receive the deadzone patch.
        """
        return bool(self.deadzone_nodes)

    @property
    def deadzone_enabled(self):
        """
        This location's deadzone is enabled if at least one deadzone node exists and
        for ANY existing deadzone node, either:
        (a) it does not have an associated config option
        (b) its associated config option indicates that the deadzone should be applied
        """
        settings = Settings()

        return any(
            [
                node.config_option is None
                # common-config options must default to True. This means options must be
                # worded in such a way that setting to False will enable the deadzones
                or settings.config.get(node.config_option) is False
                for node in self.deadzone_nodes
            ]
        )

    @property
    def is_protect_mode(self):
        """
        Check if any of the trigger nodes have protect_mode turned on.
        """
        if not self.trigger_nodes:
            return False

        return any([node.protect_mode for node in self.trigger_nodes])

    @cached_property
    def all_nodes(self):
        """
        Returns all nodes in this policy as a list
        """
        return (
            self.source_nodes
            + self.propagator_nodes
            + self.trigger_nodes
            + self.deadzone_nodes
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name})>"
