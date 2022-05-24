# -*- coding: utf-8 -*-
from plone.z3cform.fieldsets.interfaces import IDescriptiveGroup
from plone.z3cform.fieldsets.interfaces import IGroupFactory
from z3c.form import group
from zope.interface import implementer


@implementer(IDescriptiveGroup)
class Group(group.Group):
    __name__ = u""
    label = u""
    description = u""
    order = 0

    def getContent(self):
        # Default to sharing content with parent
        return self.__parent__.getContent()


@implementer(IGroupFactory)
class GroupFactory(object):

    def __init__(
        self,
        __name__,
        fields,
        label=None,
        description=None,
        order=None
    ):
        self.__name__ = __name__
        self.fields = fields
        self.label = label or __name__
        self.description = description
        self.order = order

    def __call__(self, context, request, parentForm):
        groupclass = getattr(parentForm, 'group_class', Group)
        group = groupclass(context, request, parentForm)
        group.__name__ = self.__name__
        group.label = self.label
        group.description = self.description
        group.fields = self.fields
        group.order = self.order
        return group
