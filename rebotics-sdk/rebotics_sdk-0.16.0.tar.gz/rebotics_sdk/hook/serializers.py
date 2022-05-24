from rest_framework import serializers

from rebotics_sdk.hook.signals import EVENTS


class WebhookPayloadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()


class WebhookDataSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=EVENTS)
    payload = WebhookPayloadSerializer()
