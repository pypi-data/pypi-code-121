from rest_framework import serializers

from ipam.api.serializers import NestedPrefixSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import AppSystem, AppSystemAssignment
from drf_yasg.utils import swagger_serializer_method
from django.contrib.auth.models import ContentType
from netbox.api import ContentTypeField
from utilities.api import get_serializer_for_model


class NestedAppSystemSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_app_systems-api:appsystem-detail')

    class Meta:
        model = AppSystem
        fields = ('id', 'url', 'display', 'name')


class AppSystemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_app_systems-api:appsystem-detail')

    class Meta:
        model = AppSystem
        fields = ('id', 'url', 'display', 'name', "description",
                  'comments', 'tags', 'custom_fields', 'created', 'last_updated')


class NestedAppSystemAssignmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_app_systems-api:appsystemassignment-detail')
    app_system = NestedAppSystemSerializer()

    class Meta:
        model = AppSystemAssignment
        fields = ['id', 'url', 'display', 'AppSystem', 'relation']


class AppSystemAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_app_systems-api:appsystemassignment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    object = serializers.SerializerMethodField(read_only=True)
    app_system = NestedAppSystemSerializer()

    class Meta:
        model = AppSystemAssignment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'object', 'app_system', 'created',
            'last_updated',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_object(self, instance):
        serializer = get_serializer_for_model(
            instance.content_type.model_class(), prefix='Nested')
        context = {'request': self.context['request']}
        return serializer(instance.object, context=context).data
