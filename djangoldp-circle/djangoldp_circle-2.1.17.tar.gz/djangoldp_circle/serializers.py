from rest_framework import serializers
from djangoldp_circle.models import CircleAccessRequest


class CircleAccessRequestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleAccessRequest
        fields = '__all__'
