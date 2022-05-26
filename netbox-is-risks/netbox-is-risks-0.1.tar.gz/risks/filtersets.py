import django_filters
from netbox.filtersets import ChangeLoggedModelFilterSet
from utilities.filters import ContentTypeFilter
from .models import *


class RiskAssignmentFilterSet(ChangeLoggedModelFilterSet):
    content_type = ContentTypeFilter()
    risk_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Risk.objects.all(),
        label='Risk (ID)',
    )
    relation_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RiskRelation.objects.all(),
        label='Risk relation (ID)',
    )
    relation = django_filters.ModelMultipleChoiceFilter(
        field_name='relation__name',
        queryset=RiskRelation.objects.all(),
        to_field_name='name',
        label='Risk relation (name)',
    )

    class Meta:
        model = RiskAssignment
        fields = ['id', 'content_type_id', 'object_id']
