from uuid import (
    UUID,
)

from rest_framework.generics import (
    get_object_or_404,
)

from m3_rest_gar.util import (
    is_objectguid,
)


class GUIDLookupMixin:
    """
    Миксин для вьюсета добавляет возможность получать адресный объект как
    по objectid, так и по objectguid

    Если очень захотеть, можно сюда же впихнуть поиск по коду КЛАДРа
    Но лучше такого не хотеть, да
    """

    lookup_field = 'objectid'
    guid_lookup_field = 'objectguid'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        lookup_value = self.kwargs[lookup_url_kwarg]

        if is_objectguid(lookup_value):
            lookup_field = self.guid_lookup_field
        else:
            lookup_field = self.lookup_field

        filter_kwargs = {lookup_field: lookup_value}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
