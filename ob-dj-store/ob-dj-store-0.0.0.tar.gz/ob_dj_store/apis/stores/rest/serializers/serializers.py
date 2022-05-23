import typing

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ob_dj_store.core.stores.models import (
    Attribute,
    AttributeChoice,
    Cart,
    CartItem,
    Category,
    OpeningHours,
    Order,
    OrderItem,
    Product,
    ProductAttribute,
    ProductMedia,
    ProductTag,
    ProductVariant,
    Store,
)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = (
            "id",
            "cart",
            "product_variant",
            "quantity",
            "unit_price",
            "total_price",
        )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = (
            "customer",
            "items",
            "total_price",
        )
        read_only_fields = ("id", "total_price")

    def update(self, instance, validated_data):
        instance.items.all().delete()
        # update or create instance items
        for item in validated_data["items"]:
            CartItem.objects.create(
                cart=instance,
                product_variant=item["product_variant"],
                quantity=item["quantity"],
            )
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "description", "is_active")


class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):

    opening_hours = OpeningHourSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = (
            "name",
            "address",
            "location",
            "is_active",
            "currency",
            "minimum_order_amount",
            "delivery_charges",
            "min_free_delivery_amount",
            "opening_hours",
            "created_at",
            "updated_at",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "variant",
            "quantity",
            "total_amount",
            "preparation_time",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "store",
            "shipping_method",
            "payment_method",
            "shipping_address",
            "customer",
            "status",
            "items",
            "total_amount",
            "preparation_time",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "customer": {"read_only": True},
        }

    def validate(self, attrs):
        # The Cart items must not be empty
        user = self.context["request"].user
        if not user.cart.items.exists():
            raise serializers.ValidationError(_("The Cart must not be empty"))
        return super().validate(attrs)

    def create(self, validated_data: typing.Dict):
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "is_active")


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = (
            "id",
            "name",
            "text_color",
            "background_color",
        )


class AttributeChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeChoice
        fields = (
            "id",
            "name",
        )


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = (
            "id",
            "name",
        )


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)
    attribute_choices = AttributeChoiceSerializer(many=True, source="attribute_choices")

    class Meta:
        model = ProductAttribute
        fields = (
            "id",
            "name",
            "attribute",
            "attribute_choices",
        )


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "name",
            "price",
            "quantity",
            "sku",
            "is_deliverable",
            "is_active",
        )


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = (
            "id",
            "is_primary",
            "image",
            "order_value",
        )


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    store = StoreSerializer(many=False)
    variants = ProductVariantSerializer(many=True, source="product_variants")
    product_images = ProductMediaSerializer(many=True, source="images")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category",
            "slug",
            "description",
            "product_images",
            "variants",
            "store",
        )


class ProductListSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category",
            "slug",
            "description",
            "product_images",
            "store",
        )
