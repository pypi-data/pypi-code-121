import django_filters
from netbox.filtersets import ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from utilities.filters import ContentTypeFilter
from .models import *
from django.db.models import Q


class AppSystemFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AppSystem
        fields = ['id', 'name', 'slug', 'description', 'comments']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class AppSystemAssignmentFilterSet(ChangeLoggedModelFilterSet):
    content_type = ContentTypeFilter()
    app_system_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AppSystem.objects.all(),
        label='AppSystem (ID)',
    )

    class Meta:
        model = AppSystemAssignment
        fields = ['id', 'content_type_id', 'object_id']
