from django.template import Library, Node
from django.forms import ChoiceField, MultipleChoiceField, ModelChoiceField, ModelMultipleChoiceField
from django.forms.boundfield import BoundWidget
from collections.abc import Iterable

register = Library()

@register.simple_tag
def get_selected_options(form, field_name, *sort_clauses):
    bound_field = form[field_name]

    if not isinstance(bound_field.field, ChoiceField):
        return []

    value = bound_field.value()
    if not isinstance(value, Iterable) or isinstance(value, str):
        value = [value]

    if isinstance(bound_field.field, ModelChoiceField) or isinstance(bound_field.field, MultipleChoiceField):
        selected_queryset = bound_field.field.queryset.filter(pk__in=value)
        if sort_clauses:
            selected_queryset = selected_queryset.order_by(*sort_clauses)
        choices = [(instance.pk, str(instance)) for instance in selected_queryset]
    else:
        choices = filter(lambda x : x[0] in value, bound_field.field.widget.choices)
    bound_field.field.widget.choices = choices
    return bound_field.subwidgets




