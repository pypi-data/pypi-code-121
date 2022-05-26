from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_app_systems'

router = NetBoxRouter()
router.register('app-systems', views.AppSystemViewSet)
router.register('appsystem_assignment', views.AppSystemAssignmentViewSet)

urlpatterns = router.urls