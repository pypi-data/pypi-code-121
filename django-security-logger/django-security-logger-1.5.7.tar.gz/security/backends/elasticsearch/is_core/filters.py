from django.contrib.auth import get_user_model
from django.db import router
from django.db.models import TextField
from django.db.models.functions import Cast
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType

from elasticsearch_dsl import Q

from pyston.contrib.elasticsearch.filters import ElasticsearchFilter
from pyston.filters.utils import OperatorSlug
from pyston.filters.exceptions import FilterValueError

from is_core.contrib.elasticsearch.filters import CoreElasticsearchFilterManagerFilterManager

from security.config import settings
from security.backends.elasticsearch.models import get_key_from_content_type_object_id_and_model_db


class UsernameUserFilter(ElasticsearchFilter):

    allowed_operators = (OperatorSlug.CONTAINS,)

    def clean_value(self, value, operator_slug, request):
        user_model = get_user_model()
        queryset = user_model.objects.filter(
            **{'{}__contains'.format(user_model.USERNAME_FIELD): value}
        ).annotate(
            str_id=Cast('id', output_field=TextField())
        )

        if queryset[:settings.ELASTICSERACH_MAX_NUMBER_OF_TERMS].count() > settings.ELASTICSERACH_MAX_NUMBER_OF_TERMS:
            raise FilterValueError(ugettext('Too many users found for specified username.'))

        return list(queryset.values_list('str_id', flat=True))

    def get_filter_term(self, value, operator_slug, request):
        return Q('terms', **{'user_id': value})


class EnumElasticsearchFilter(ElasticsearchFilter):

    allowed_operators = (OperatorSlug.EQ,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum = self.field._enum
        self.choices = [(None, '')] + [
            (choice.name, choice.label) for choice in self._enum
        ]

    def clean_value(self, value, operator_slug, request):
        try:
            return self._enum[value]
        except KeyError:
            raise FilterValueError(
                ugettext('Invalid value. Please use one of the following values: {}.').format(
                    ', '.join([a.name for a in self._enum])
                )
            )

    def get_filter_term(self, value, operator_slug, request):
        return Q('term', **{self.get_full_filter_key(): value.name})


class SecurityElasticsearchFilterManager(CoreElasticsearchFilterManagerFilterManager):

    filter_by_field_name = {
        'enum': EnumElasticsearchFilter,
        **CoreElasticsearchFilterManagerFilterManager.filter_by_field_name,
    }


class RelatedObjectsFilter(ElasticsearchFilter):

    allowed_operators = (OperatorSlug.IN,)

    def clean_value(self, value, operator_slug, request):
        cleaned_values = []
        for v in value:
            try:
                content_type_id, object_id = v.split('|')

                content_type = ContentType.objects.get(pk=content_type_id)
                model_db = router.db_for_write(content_type.model_class())

                cleaned_values.append(
                    get_key_from_content_type_object_id_and_model_db(model_db, content_type_id, object_id)
                )
            except (ValueError, ContentType.DoesNotExist):
                raise FilterValueError(ugettext('Invalid value.'))
        return cleaned_values

    def get_filter_term(self, value, operator_slug, request):
        return Q('terms', related_objects=value)
