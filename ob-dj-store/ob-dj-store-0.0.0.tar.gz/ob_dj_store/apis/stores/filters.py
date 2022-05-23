from django_filters import rest_framework as filters

from ob_dj_store.core.stores.models import Product, ProductVariant, Store


class StoreFilter(filters.FilterSet):
    """Store filters"""

    location = filters.CharFilter(method="by_location")

    class Meta:
        model = Store
        fields = [
            "location",
            "delivery_charges",
            "min_free_delivery_amount",
        ]

    def by_location(self, queryset, name, value):
        return queryset.filter(poly__contains=value)


class ProductFilter(filters.FilterSet):
    """Product filters"""

    class Meta:
        model = Product
        fields = [
            "store__name",
            "category__name",
        ]


class VariantFilter(filters.FilterSet):
    """Variant filters"""

    class Meta:
        model = ProductVariant
        fields = [
            "product__name",
            "product__category__name",
        ]
