from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from ob_dj_store.apis.stores.views import (
    CartView,
    CategoryViewSet,
    OrderView,
    ProductView,
    StoreView,
    VariantView,
)

app_name = "stores"

router = SimpleRouter(trailing_slash=False)

router.register(r"", StoreView, basename="store")
router.register(r"cart", CartView, basename="cart")
router.register(r"order", OrderView, basename="order")
router.register(r"product", ProductView, basename="product")
router.register(r"variant", VariantView, basename="variant")
router.register(r"category", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
