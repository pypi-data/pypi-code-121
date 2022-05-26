# encoding: utf-8
from __future__ import absolute_import

import six

from rapyuta_io.utils import ObjDict, ComponentNotFoundException
from rapyuta_io.utils.utils import is_empty


class Plan(ObjDict):
    """
    Plan class represents a plan in the package. Member variables of the class represent the
    properties of the plan.

    :ivar planId: (full-only) Plan Id.
    :ivar planName: (full-only) Plan Name.
    :ivar packageId: (full-only) Package Id.
    :ivar description: Plan Description.
    :ivar singleton: (full-only) Boolean representing whether the plan is singelton or not.
    :ivar inboundROSInterfaces: (full-only) Dictionary containing inbound ROS interfaces information.
    :ivar dependentDeployments: (full-only) List of other dependent deployments.
    :ivar components: (full-only) Dictionary containing components such as executables.
    :ivar internalComponents: (full-only) Dictionary containing internal components information.
    :ivar metadata: List containing plan metadata.
    :ivar CreatedAt: (full-only) Date of creation.
    :ivar UpdatedAt: (full-only) Date of updation.
    :ivar DeletedAt: (full-only) Date of deletion.

    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)
        if 'planId' in self:
            self.planId = self.planId
        else:
            self.planId = self.id
        self._component_id_map = dict()
        self._map_component_id_with_name()
        self._needs_alias = None

    def _map_component_id_with_name(self):
        if not hasattr(self, 'internalComponents'):
            raise ComponentNotFoundException('Internal components not found for the plan: %s(%s)'
                                             % (self.planName, self.planId))
        for component in self.internalComponents:
            self._component_id_map[component['componentName']] = component['componentId']

    def get_component_id(self, component_name):
        component_id = self._component_id_map.get(component_name)
        if is_empty(component_id):
            raise ComponentNotFoundException('Component %s is not found' % component_name)
        return component_id

    def get_component_by_name(self, component_name):
        for component in self.components.components:
            if component.name == component_name:
                return component
        return None

    def _has_inbound_targeted(self):
        try:
            if hasattr(self.inboundROSInterfaces.inboundROSInterfaces, 'anyIncomingScopedOrTargetedRosConfig') and \
                    self.inboundROSInterfaces.inboundROSInterfaces.anyIncomingScopedOrTargetedRosConfig:
                return True
            for topic in self.inboundROSInterfaces.inboundROSInterfaces.topics:
                if isinstance(topic.targeted, bool) and topic.targeted:
                    return True
                if isinstance(topic.scoped, six.string_types):
                    if topic.scoped.lower() == 'true':
                        return True
            for service in self.inboundROSInterfaces.inboundROSInterfaces.services:
                if isinstance(service.targeted, bool) and service.targeted:
                    return True
                if isinstance(service.scoped, six.string_types):
                    if service.scoped.lower() == 'true':
                        return True
            for action in self.inboundROSInterfaces.inboundROSInterfaces.actions:
                if isinstance(action.targeted, bool) and action.targeted:
                    return True
                if isinstance(action.scoped, six.string_types):
                    if action.scoped.lower() == 'true':
                        return True
        except AttributeError:
            pass
        return False

    def _has_oubound_scoped_targeted(self):
        if not hasattr(self, 'components'):
            return False
        if not hasattr(self.components, 'components'):
            return False
        for component in self.components.components:
            if not hasattr(component, 'ros'):
                continue
            for entity in ['topics', 'services', 'actions']:
                entity_list = getattr(component.ros, entity, [])
                for element in entity_list:
                    if hasattr(element, 'targeted'):
                        if isinstance(element.targeted, bool) and element.targeted:
                            return True
                        if isinstance(element.targeted, six.string_types):
                            if element.scoped.lower() == 'true':
                                return True
                    if hasattr(element, 'scoped'):
                        if isinstance(element.scoped, bool) and element.scoped:
                            return True
                        if isinstance(element.scoped, six.string_types):
                            if element.scoped.lower() == 'true':
                                return True
        return False

    def needs_aliases(self):
        if self._needs_alias is not None:
            return self._needs_alias
        self._needs_alias = (self._has_inbound_targeted() or self._has_oubound_scoped_targeted())
        return self._needs_alias

    def validate(self):
        for component in self.config.component_parameters.keys():
            for param in self.config.component_parameters[component]:
                if self.config.component_parameters[component][param] is None:
                    raise ValueError(
                        "Value of parameter %s of component %s not provided" % (
                            param, component))
