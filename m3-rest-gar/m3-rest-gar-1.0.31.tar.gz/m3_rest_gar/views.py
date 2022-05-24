from rest_framework import (
    viewsets,
)

from m3_gar.models import (
    AddrObj,
    Apartments,
    Houses,
    Steads,
    Rooms,
)
from m3_rest_gar.filters import (
    AddrObjFilter,
    ApartmentsFilter,
    HousesFilter,
    SteadsFilter,
    RoomsFilter,
)
from m3_rest_gar.mixins import (
    GUIDLookupMixin,
)
from m3_rest_gar.serializers import (
    AddrObjSerializer,
    ApartmentsSerializer,
    HousesSerializer,
    SteadsSerializer,
    RoomsSerializer,
)


class BaseAddrObjReadOnlyViewSet(GUIDLookupMixin, viewsets.ReadOnlyModelViewSet):
    pass


class AddrObjViewSet(BaseAddrObjReadOnlyViewSet):
    queryset = AddrObj.objects.filter(
        isactive=True,
        isactual=True,
    ).select_related(
        'objectid',
    ).order_by(
        'level',
        'objectid',
    )

    serializer_class = AddrObjSerializer
    filterset_class = AddrObjFilter


class HousesViewSet(BaseAddrObjReadOnlyViewSet):
    queryset = Houses.objects.filter(
        isactive=True,
        isactual=True,
    ).select_related(
        'objectid',
        'housetype',
        'addtype1',
        'addtype2',
    ).order_by(
        'objectid',
    )

    serializer_class = HousesSerializer
    filterset_class = HousesFilter


class SteadsViewSet(BaseAddrObjReadOnlyViewSet):
    queryset = Steads.objects.filter(
        isactive=True,
        isactual=True,
    ).select_related(
        'objectid',
    ).order_by(
        'objectid',
    )

    serializer_class = SteadsSerializer
    filterset_class = SteadsFilter


class ApartmentsViewSet(BaseAddrObjReadOnlyViewSet):
    queryset = Apartments.objects.filter(
        isactive=True,
        isactual=True,
    ).select_related(
        'objectid',
        'aparttype',
    ).order_by(
        'objectid',
    )

    serializer_class = ApartmentsSerializer
    filterset_class = ApartmentsFilter


class RoomsViewSet(BaseAddrObjReadOnlyViewSet):
    queryset = Rooms.objects.filter(
        isactive=True,
        isactual=True,
    ).select_related(
        'objectid',
        'roomtype',
    ).order_by(
        'objectid',
    )

    serializer_class = RoomsSerializer
    filterset_class = RoomsFilter
