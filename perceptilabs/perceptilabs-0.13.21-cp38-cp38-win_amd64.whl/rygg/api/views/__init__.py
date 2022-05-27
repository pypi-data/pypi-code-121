from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rygg import settings
from rygg import __version__
from rygg.api.app import updates_available


@api_view(["GET"])
@permission_classes([AllowAny])
def get_version(request):
    return Response({"version": __version__})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_updates_available(request):
    return Response({"newer_versions": updates_available()})


@api_view(["GET"])
@permission_classes([AllowAny])
def is_enterprise(request):
    return Response({"is_enterprise": settings.IS_CONTAINERIZED})
