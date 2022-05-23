from django.db.models import Q
from django.conf import settings
from djangoldp.utils import is_anonymous_user
from djangoldp.filters import LDPPermissionsFilterBackend
from djangoldp_circle.xmpp import get_client_ip, XMPP_SERVERS
from rest_framework_guardian.filters import ObjectPermissionsFilter
from guardian.utils import get_anonymous_user


class CircleFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        if get_client_ip(request) in XMPP_SERVERS:
            return queryset
        elif is_anonymous_user(request.user):
            return queryset.filter(status='Public')
        else:
            objects = super().filter_queryset(request, queryset, view).values_list('pk')
            return queryset.filter(
                Q(members__user=request.user) |
                Q(status='Public') |
                Q(status='Restricted') |
                Q(pk__in=objects)
            ).distinct()


class CircleMemberFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        if get_client_ip(request) in XMPP_SERVERS:
            return queryset
        elif is_anonymous_user(request.user):
            return view.model.objects.none()
        else:
            objects = super().filter_queryset(request, queryset, view).values_list('pk')
            return queryset.filter(
                Q(user=request.user) |
                Q(circle__status='Public') |
                Q(circle__members__user=request.user) |
                Q(pk__in=objects)
            ).distinct()


class CircleAccessRequestFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        from djangoldp_circle.models import CircleMember

        if get_client_ip(request) in XMPP_SERVERS:
            return queryset
        elif is_anonymous_user(request.user):
            return view.model.objects.none()
        else:
            # objects which I have permissions on by grace of my superclass (e.g. object permissions)
            objects = super().filter_queryset(request, queryset, view).values_list('pk', flat=True)
            # unite it with the circles for which I am an administrator
            objects = list(set(objects).union(CircleMember.objects.filter(user=request.user, is_admin=True).values_list('circle', flat=True)))

            return queryset.filter(
                Q(user=request.user) |
                Q(pk__in=objects)
            ).distinct()
