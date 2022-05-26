
from copy import copy

from django.db import models

from model_search import model_search
from tecdoc.utils import clean_code


class ProductQuerySet(models.QuerySet):

    def search(
            self,
            code=None,
            bar_code=None,
            category=None,
            query=None):

        queryset = copy(self)

        if category:
            queryset = queryset.filter(category=category)

        if code:
            queryset = queryset.filter(clean_code=clean_code(code))

        if bar_code:
            value = bar_code

            if value.startswith('000') and len(value) == 12:
                value = value[:-1]

            queryset = queryset.filter(bar_code__icontains=value)

        if query:
            queryset = model_search(query, queryset, ['name'])

        return queryset

    def active(self):
        return self.filter(is_active=True)
