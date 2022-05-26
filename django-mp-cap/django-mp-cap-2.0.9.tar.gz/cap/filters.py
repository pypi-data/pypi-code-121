
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.filters import SimpleListFilter, FieldListFilter


class InputFilter(SimpleListFilter):

    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class IsNullFieldListFilter(FieldListFilter):

    notnull_label = _('Is present')
    isnull_label = _('Is Null')

    def __init__(
            self,
            field,
            request,
            params,
            model,
            model_admin,
            field_path):

        self.lookup_kwarg = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

        super().__init__(
            field,
            request,
            params,
            model,
            model_admin,
            field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        choices = (
            (None, _('All')),
            ('False', self.notnull_label),
            ('True', self.isnull_label),
        )
        for lookup, title in choices:
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: lookup,
                }),
                'display': title,
            }
