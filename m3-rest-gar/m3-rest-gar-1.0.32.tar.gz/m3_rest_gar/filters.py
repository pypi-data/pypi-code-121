import operator
from functools import (
    reduce,
)

from django.db.models import (
    Q,
)
from django_filters.rest_framework import (
    BaseInFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
)

from m3_gar.models import (
    AddrObj,
    Apartments,
    Houses,
    Steads,
    Rooms,
)
from m3_rest_gar.util import (
    get_hierarchy_models,
    is_objectguid,
)


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CharInFilter(BaseInFilter, CharFilter):
    pass


class HierarchyFilter(CharFilter):
    """
    Фильтр в иерархии адресных объектов.
    На входе ожидается строка вида `hierarchy:filter_str`,
    где hierarchy - название иерархии, filter_str - значение,
    по которому нужно фильтровать. Класс-наследник определяет
    поведение фильтра для filter_str.
    """

    def filter(self, qs, value):
        if value:
            try:
                hierarchy, filter_str = value.split(':')
            except ValueError:
                pass
            else:
                filter_expression = Q()

                for hierarchy_model in get_hierarchy_models(hierarchy):
                    filter_for_hierarchy = self.get_filter_for_hierarchy(hierarchy_model, filter_str)
                    if filter_for_hierarchy:
                        filter_expression |= filter_for_hierarchy

                qs = qs.filter(filter_expression)

        return qs

    def get_filter_for_hierarchy(self, hierarchy_model, filter_value):
        """Возвращает фильтр по переданному значению для модели иерархии.

        Args:
            hierarchy_model: Класс модели иерархии
            filter_value: Строковое значение, по которому нужно фильтровать

        Returns:
            Выражение, содержащее необходимые фильтры
        """

        return Q()


class HierarchyParentFilter(HierarchyFilter):
    """
    Фильтр по objectid родителя в иерархии адресных объектов.
    На вход фильтра ожидается строка вида `hierarchy:parentobjid`
    """

    def get_filter_for_hierarchy(self, hierarchy_model, filter_value):
        if is_objectguid(filter_value):
            filter_key = 'parentobjid__objectguid'
        else:
            filter_key = 'parentobjid__objectid'

        return Q(
            objectid__in=hierarchy_model.objects.filter(**{
                'isactive': True,
                filter_key: filter_value,
            }).values('objectid'),
        )


class HierarchyNameWithParentsFilter(HierarchyFilter):
    """
    Фильтр по полю name_with_parents в иерархии адресных объектов.
    На вход фильтра ожидается строка вида `hierarchy:str_value`
    """

    def get_filter_for_hierarchy(self, hierarchy_model, filter_value):
        filter_parts = [value.strip() for value in filter_value.split(',') if value]
        hierarchy_filter = Q(isactive=True)

        for part in filter_parts:
            hierarchy_filter &= Q(name_with_parents__icontains=part)

        return Q(
            objectid__in=hierarchy_model.objects.filter(hierarchy_filter).values('objectid'),
        )


class AddrObjFilter(FilterSet):
    """
    Фильтр сведений классификатора адресообразующих элементов
    """
    level = NumberInFilter(field_name='level')
    parent = HierarchyParentFilter()
    region_code = NumberInFilter(field_name='region_code')
    name = CharFilter(lookup_expr='icontains')
    name__exact = CharFilter(lookup_expr='exact')
    name_with_typename = CharFilter(lookup_expr='icontains')
    typename = CharInFilter(field_name='typename')
    name_with_parents = HierarchyNameWithParentsFilter()

    class Meta:
        model = AddrObj
        fields = ['level', 'parent', 'name', 'name__exact', 'name_with_typename', 'typename']


class HousesFilter(FilterSet):
    """
    Фильтр сведений по номерам домов улиц городов и населенных пунктов
    """
    parent = HierarchyParentFilter()
    housenum = CharFilter(method='_housenum', lookup_expr='icontains')
    housenum__exact = CharFilter(method='_housenum', lookup_expr='exact')

    class Meta:
        model = Houses
        fields = ['parent', 'housenum', 'housenum__exact']

    def _housenum(self, qs, name, value):
        """
        Фильтр по номеру дома также должен учитывать дополнительные номера дома
        """
        filter_field = self.filters[name]
        lookup_expr = filter_field.lookup_expr

        fields = ['housenum', 'addnum1', 'addnum2']
        filters = [
            Q(**{
                f'{field}__{lookup_expr}': value,
            }) for field in fields
        ]
        q = reduce(operator.or_, filters, Q())
        qs = qs.filter(q)

        return qs


class SteadsFilter(FilterSet):
    """
    Фильтр сведений по земельным участкам
    """

    parent = HierarchyParentFilter()
    number = CharFilter(lookup_expr='icontains')
    number__exact = CharFilter(lookup_expr='exact')

    class Meta:
        model = Steads
        fields = ['parent', 'number', 'number__exact']


class ApartmentsFilter(FilterSet):
    """
    Фильтр сведений по помещениям
    """
    parent = HierarchyParentFilter()
    number = CharFilter(lookup_expr='icontains')
    number__exact = CharFilter(lookup_expr='exact')

    class Meta:
        model = Apartments
        fields = ['parent', 'number', 'number__exact']


class RoomsFilter(FilterSet):
    """
    Фильтр сведений по комнатам
    """
    parent = HierarchyParentFilter()
    number = CharFilter(lookup_expr='icontains')
    number__exact = CharFilter(lookup_expr='exact')

    class Meta:
        model = Rooms
        fields = ['parent', 'number', 'number__exact']
