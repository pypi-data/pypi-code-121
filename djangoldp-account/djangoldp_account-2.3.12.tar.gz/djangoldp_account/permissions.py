from django.conf import settings

from djangoldp.permissions import LDPPermissions
from djangoldp.utils import is_anonymous_user


XMPP_SERVERS = set({'51.15.243.248', '212.47.234.179', '2001:bc8:47b0:2711::1'})

if hasattr(settings, 'XMPP_SERVER_IP'):
    XMPP_SERVERS = XMPP_SERVERS.union(getattr(settings, 'XMPP_SERVER_IP'))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class LDPUserPermissions(LDPPermissions):

    def has_permission(self, request, view):
        if get_client_ip(request) in XMPP_SERVERS:
            return True

        return super().has_permission(request, view)

    def get_container_permissions(self, request, view, obj=None):
        '''analyses the Model's set anonymous, authenticated and owner_permissions and returns these'''
        from djangoldp.models import Model

        model = view.model
        anonymous_perms, authenticated_perms, owner_perms, superuser_perms = self.get_permission_settings(model)
        perms = super().get_container_permissions(request, view, obj)
        if is_anonymous_user(request.user):
            if get_client_ip(request) in XMPP_SERVERS:
                perms = perms.union(set(['view']))
            else:
                perms = perms.union(set(anonymous_perms))
        else:
            if obj is not None and Model.is_owner(view.model, request.user, obj):
                perms = perms.union(set(owner_perms))
            else:
                perms = perms.union(set(authenticated_perms))

            if request.user.is_superuser:
                perms = perms.union(set(superuser_perms))
        return perms

    def has_container_permission(self, request, view):

        if get_client_ip(request) in XMPP_SERVERS:
            return True

        return super().has_container_permission(request, view)

    def has_permission(self, request, view):
        """concerned with the permissions to access the _view_"""
        if is_anonymous_user(request.user):
            if not self.has_container_permission(request, view):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        if get_client_ip(request) in XMPP_SERVERS:
            return True

        return super().has_object_permission(request, view, obj)
