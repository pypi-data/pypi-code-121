from attr import fields
from graphene import ObjectType
from netbox.graphql.types import NetBoxObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from . import filtersets
from .models import Risk, RiskRelation, RiskAssignment


class RiskType(NetBoxObjectType):
    class Meta:
        model = Risk
        fields = '__all__'


class RiskRelationType(NetBoxObjectType):
    class Meta:
        model = RiskRelation
        fields = '__all__'


class RiskAssingmentType(NetBoxObjectType):
    class Meta:
        model = RiskAssignment
        fields = '__all__'
        filterset_class = filtersets.RiskAssignmentFilterSet


class Query(ObjectType):
    risk = ObjectField(RiskType)
    risk_list = ObjectListField(RiskType)
    relation = ObjectField(RiskRelationType)
    relation_list = ObjectListField(RiskRelationType)
    risk_assignment = ObjectField(RiskAssingmentType)
    risk_assignment_list = ObjectListField(RiskAssingmentType)


schema = Query
