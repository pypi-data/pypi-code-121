from rest_framework import permissions
from django.conf import settings


class HasAuthToken(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_PARSAGON_API_KEY') == settings.API_KEY
