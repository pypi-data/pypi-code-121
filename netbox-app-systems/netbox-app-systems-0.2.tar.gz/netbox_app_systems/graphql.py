from attr import fields
from graphene import ObjectType
from netbox.graphql.types import NetBoxObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from . import filtersets, models


class AppSystemType(NetBoxObjectType):
    class Meta:
        model = models.AppSystem
        fields = '__all__'


class AppSystemAssignmentType(NetBoxObjectType):
    class Meta:
        model = models.AppSystemAssignment
        fields = '__all__'
        filterset_class = filtersets.AppSystemAssignmentFilterSet


class Query(ObjectType):
    app_system = ObjectField(AppSystemType)
    app_system_list = ObjectListField(AppSystemType)
    app_system_assignment = ObjectField(AppSystemAssignmentType)
    app_system_assignment_list = ObjectListField(AppSystemAssignmentType)


schema = Query
