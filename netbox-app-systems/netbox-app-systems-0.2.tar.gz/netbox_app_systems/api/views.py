from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from .serializers import AppSystemSerializer, AppSystemAssignmentSerializer
from .. import filtersets

class AppSystemViewSet(NetBoxModelViewSet):
    queryset = models.AppSystem.objects.prefetch_related('tags')
    serializer_class = AppSystemSerializer


class AppSystemAssignmentViewSet(NetBoxModelViewSet):
    queryset = models.AppSystemAssignment.objects.prefetch_related(
        'object', 'app_system')
    serializer_class = AppSystemAssignmentSerializer
    filterset_class = filtersets.AppSystemAssignmentFilterSet
