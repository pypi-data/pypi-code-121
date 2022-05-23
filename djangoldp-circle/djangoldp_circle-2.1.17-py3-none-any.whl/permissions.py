from django.conf import settings
from django.db.models import QuerySet, Q

from djangoldp.utils import is_authenticated_user
from djangoldp.permissions import LDPPermissions, LDPObjectLevelPermissions
from djangoldp_circle.filters import CircleFilterBackend, CircleMemberFilterBackend, \
    CircleAccessRequestFilterBackend
from djangoldp_circle.xmpp import get_client_ip, XMPP_SERVERS


class CirclePermissions(LDPPermissions):
    filter_backends = [CircleFilterBackend]

    def get_object_permissions(self, request, view, obj):
        perms = super().get_object_permissions(request, view, obj)

        user = request.user
        if is_authenticated_user(user):
            # permissions gained by being a circle-member, and admin
            if obj.members.filter(user=user).exists():
                perms = perms.union({'view', 'add'})

                if obj.members.filter(user=user).get().is_admin:
                    perms = perms.union({'change', 'delete'})

        # permissions gained by the circle being public
        if obj.status == 'Public':
            perms = perms.union({'view'})

            # I can join the public circle
            if is_authenticated_user(user):
                perms = perms.union({'add'})
        
        # I can view - but not automatically join - restricted circles
        elif obj.status == 'Restricted':
            perms = perms.union({'view'})

        return perms

    def get_container_permissions(self, request, view, obj=None, bypass=False):
        if obj is None:
            perms = super().get_container_permissions(request, view, obj)

            if not request.user.is_anonymous and not bypass:
                default_perms = getattr(settings, 'USER_AUTHENTICATED_CIRCLE_PERMISSIONS', ['view', 'add'])
                perms = perms.union(set(default_perms))
        else:
            return self.get_object_permissions(request, view, obj)

        return perms
    
    def has_permission(self, request, view):
        '''if get_client_ip(request) in XMPP_SERVERS:
            return True'''

        return True
    
    def has_object_permission(self, request, view, obj):
        if get_client_ip(request) in XMPP_SERVERS:
            return True

        return super().has_object_permission(request, view, obj)


class CircleMemberPermissions(LDPPermissions):
    filter_backends = [CircleMemberFilterBackend]

    def get_object_permissions(self, request, view, obj):
        perms = super().get_object_permissions(request, view, obj)

        user = request.user

        if is_authenticated_user(user):
            # the operation is on myself
            if obj.user == user:
                perms.add('view')

                if not obj.is_admin or obj.circle.members.filter(is_admin=True).count() > 1:
                    perms.add('delete')

                if obj.circle.status == 'Public':
                    perms = perms.union({'add', 'delete'})

            # the operation is on another member
            else:
                # permissions gained in public circles
                if obj.circle.status == 'Public':
                    perms = perms.union({'view', 'add'})

                # permissions gained for all members
                if obj.circle.members.filter(user=user).exists():
                    perms = perms.union({'view', 'add'})

                    # permissions gained for admins (on other users)
                    if obj.circle.members.filter(user=user).get().is_admin \
                            and not obj.is_admin:
                        perms = perms.union({'delete', 'change'})

        return perms
    
    def has_permission(self, request, view):
        if get_client_ip(request) in XMPP_SERVERS:
            return True

        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if get_client_ip(request) in XMPP_SERVERS:
            return True

        return super().has_object_permission(request, view, obj)


class CircleAccessRequestPermissions(LDPPermissions):
    filter_backends = [CircleAccessRequestFilterBackend]

    def get_object_permissions(self, request, view, obj):
        from djangoldp_circle.models import CircleMember

        perms = super().get_object_permissions(request, view, obj)

        user = request.user
        if is_authenticated_user(user):
            # I must be an admin of the circle referenced
            member = obj.circle.members.filter(user=user)
            if member.exists() and member.get().is_admin:
                perms = perms.union({'view', 'change'})

        return perms
