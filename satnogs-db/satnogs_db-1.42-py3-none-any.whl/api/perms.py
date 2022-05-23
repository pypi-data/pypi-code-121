"""SatNOGS DB API permissions, django rest framework"""
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated


class SafeMethodsWithPermission(permissions.BasePermission):
    """Access non-destructive methods (like GET and HEAD) with API Key"""
    def has_permission(self, request, view):
        return self.has_object_permission(request, view)

    def has_object_permission(self, request, view, obj=None):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return True


class IsAuthenticatedOrOptions(IsAuthenticated):
    """Allow unauthenticated access for OPTIONS method,
       check authentication for all other methods."""
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super().has_permission(request, view)
