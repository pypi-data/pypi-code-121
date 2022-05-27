from . import models
from . import serializers
from rest_framework import viewsets, permissions


class DriverViewSet(viewsets.ModelViewSet):
    """ViewSet for the Driver class"""

    queryset = models.Driver.objects.all()
    serializer_class = serializers.DriverSerializer
    permission_classes = [permissions.IsAuthenticated]


class DriverStepViewSet(viewsets.ModelViewSet):
    """ViewSet for the DriverStep class"""

    queryset = models.DriverStep.objects.all()
    serializer_class = serializers.DriverStepSerializer
    permission_classes = [permissions.IsAuthenticated]


