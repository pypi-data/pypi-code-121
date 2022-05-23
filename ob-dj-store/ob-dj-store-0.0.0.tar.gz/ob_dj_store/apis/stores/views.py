import logging

from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, viewsets

from ob_dj_store.apis.stores.filters import ProductFilter, StoreFilter, VariantFilter
from ob_dj_store.apis.stores.rest.serializers.serializers import (
    CartSerializer,
    CategorySerializer,
    OrderSerializer,
    ProductListSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    StoreSerializer,
)
from ob_dj_store.core.stores.models import (
    Cart,
    Category,
    Order,
    Product,
    ProductVariant,
    Store,
)

logger = logging.getLogger(__name__)


class StoreView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = StoreSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    filterset_class = StoreFilter
    queryset = Store.objects.active()

    @swagger_auto_schema(
        operation_summary="List Stores",
        operation_description="""
            List Stores
        """,
        tags=[
            "Store",
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CartView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = CartSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Cart.objects.all()

    def get_object(self):
        return self.request.user.cart

    @swagger_auto_schema(
        operation_summary="Retrieve Customer Cart",
        operation_description="""
            Retrieve the current customer's cart /store/cart/me
        """,
        tags=[
            "Cart",
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Customer Cart",
        operation_description="""
            Updates the current customer's cart /store/cart/me
        """,
        tags=[
            "Cart",
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class OrderView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @swagger_auto_schema(
        operation_summary="Retrieve An Order",
        operation_description="""
            Retrieve an order by id
        """,
        tags=[
            "Order",
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List Orders",
        operation_description="""
            List Orders
        """,
        tags=[
            "Order",
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Customer Order",
        operation_description="""
            Create a customer order
        """,
        tags=[
            "Order",
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class VariantView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductVariantSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    filterset_class = VariantFilter
    queryset = ProductVariant.objects.active()

    @swagger_auto_schema(
        operation_summary="List Variants",
        operation_description="""
            List Variants
        """,
        tags=[
            "Variant",
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    filterset_class = ProductFilter
    queryset = Product.objects.active()

    @swagger_auto_schema(
        operation_summary="List Products",
        operation_description="""
            List Products
        """,
        tags=[
            "Product",
        ],
    )
    def get_serializer_class(self):
        # # TODO: Replace If logic with dict lookup
        # Listing Serializer
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List Categories",
        tags=[
            "Category",
        ],
        responses={200: openapi.Response("list_categories", CategorySerializer)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Retrieve Category",
        tags=[
            "Category",
        ],
        responses={200: openapi.Response("retrieve_categories", CategorySerializer)},
    ),
)
class CategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    http_method_names = ["get"]
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Category.objects.active()
