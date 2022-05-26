from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import Risk, RiskRelation, RiskAssignment
from django.contrib.auth.models import ContentType
from drf_yasg.utils import swagger_serializer_method
from netbox.api import ChoiceField, ContentTypeField
from utilities.api import get_serializer_for_model


class NestedRiskSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:risks-api:risk-detail'
    )

    class Meta:
        model = Risk
        fields = ('id', 'display', 'url', 'name', 'description')


class RiskSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:risks-api:risk-detail'
    )

    class Meta:
        model = Risk
        fields = ('id', 'url', 'display', 'name', 'description')


class NestedRiskRelationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:risks-api:riskrelation-detail'
    )

    class Meta:
        model = RiskRelation
        fields = ('id', 'url', 'display', 'name', 'description')


class RiskRelationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:risks-api:riskrelation-detail'
    )

    class Meta:
        model = RiskRelation
        fields = ('id', 'url', 'display', 'name', 'description')


class NestedRiskAssignmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:risks-api:riskassignment-detail')
    risk = NestedRiskSerializer()
    relation = NestedRiskRelationSerializer

    class Meta:
        model = RiskAssignment
        fields = ['id', 'url', 'display', 'risk', 'relation']


class RiskAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:risks-api:riskassignment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    object = serializers.SerializerMethodField(read_only=True)
    risk = NestedRiskSerializer()
    relation = NestedRiskRelationSerializer(required=False, allow_null=True)

    class Meta:
        model = RiskAssignment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'object', 'risk', 'relation', 'created',
            'last_updated',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_object(self, instance):
        serializer = get_serializer_for_model(
            instance.content_type.model_class(), prefix='Nested')
        context = {'request': self.context['request']}
        return serializer(instance.object, context=context).data
