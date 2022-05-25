from rest_framework.filters import BaseFilterBackend
from rest_framework_guardian.filters import ObjectPermissionsFilter
from djangoldp.utils import is_anonymous_user


class LDPPermissionsFilterBackend(ObjectPermissionsFilter):
    """
    Default FilterBackend for LDPPermissions. If user does not have model-level permissions, filters by
    Django-Guardian's get_objects_for_user
    """

    shortcut_kwargs = {
        'accept_global_perms': False,
        'with_superuser': True
    }

    def filter_queryset(self, request, queryset, view):
        from djangoldp.models import Model
        from djangoldp.permissions import LDPPermissions, ModelConfiguredPermissions

        # compares the requirement for GET, with what the user has on the container
        configured_permission_classes = Model.get_permission_classes(view.model, [LDPPermissions])
        for permission_class in [p() for p in configured_permission_classes]:
            # inherits from LDPBasePermissions
            if hasattr(permission_class, 'has_container_permission') and \
                permission_class.has_container_permission(request, view):

                return queryset

        # the user did not have permission on the container, so now we filter the queryset for permissions on the object
        if not is_anonymous_user(request.user):
            # those objects I have by grace of group or object
            # first figure out if the superuser has special permissions (important to the implementation in superclass)
            perms_class = ModelConfiguredPermissions()
            anon_perms, auth_perms, owner_perms, superuser_perms = perms_class.get_permission_settings(view.model)
            self.shortcut_kwargs['with_superuser'] = 'view' in superuser_perms

            object_perms = super().filter_queryset(request, queryset, view)

            # those objects I have by grace of being owner
            if Model.get_meta(view.model, 'owner_field', None) is not None:
                if 'view' in owner_perms:
                    owned_objects = [q.pk for q in queryset if Model.is_owner(view.model, request.user, q)]
                    return object_perms | queryset.filter(pk__in=owned_objects)
            return object_perms

        # user is anonymous without anonymous permissions
        return view.model.objects.none()


class LocalObjectFilterBackend(BaseFilterBackend):
    """
    Filter which removes external objects (federated backlinks) from the queryset
    For querysets which should only include local objects
    """
    def filter_queryset(self, request, queryset, view):
        from djangoldp.models import Model

        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


class LocalObjectOnContainerPathBackend(LocalObjectFilterBackend):
    """
    Override of LocalObjectFilterBackend which removes external objects when the view requested
    is the model container path
    """
    def filter_queryset(self, request, queryset, view):
        from djangoldp.models import Model

        if issubclass(view.model, Model) and request.path_info == view.model.get_container_path():
            return super(LocalObjectOnContainerPathBackend, self).filter_queryset(request, queryset, view)
        return queryset
