from rest_framework import (
    routers,
)

from django.urls import (
    include,
    path,
)

from m3_rest_gar.views import (
    AddrObjViewSet,
    ApartmentsViewSet,
    HousesViewSet,
    SteadsViewSet,
    RoomsViewSet,
)


router = routers.DefaultRouter()
router.register('addrobj', AddrObjViewSet, basename='addrobj')
router.register('houses', HousesViewSet, basename='houses')
router.register('steads', SteadsViewSet, basename='steads')
router.register('apartments', ApartmentsViewSet, basename='apartments')
router.register('rooms', RoomsViewSet, basename='rooms')


urlpatterns = [
    path('v1/', include(router.urls)),
]
