from django.contrib.contenttypes.models import ContentType
from django.db import models


class ActiveMixin:
    def active(self):
        return self.filter(is_active=True)


class StoreManager(ActiveMixin, models.Manager):
    pass


class CategoryManager(ActiveMixin, models.Manager):
    pass


class ProductVariantManager(ActiveMixin, models.Manager):
    pass


class ProductManager(ActiveMixin, models.Manager):
    pass


class CartManager(models.Manager):
    pass


class CartItemManager(models.Manager):
    pass


class ShippingMethodManager(ActiveMixin, models.Manager):
    pass


class PaymentMethodManager(ActiveMixin, models.Manager):
    pass


class OrderPaymentManager(models.Manager):
    pass


class OrderManager(models.Manager):
    def create(self, *args, **kwargs):
        order = super().create(**kwargs)
        for item in order.customer.cart.items.all():
            order.items.create(
                variant=item.product_variant,
                quantity=item.quantity,
            )
            item.delete()
        return order


class FavoriteManager(ActiveMixin, models.Manager):
    def favorites_for_user(self, user):
        """Returns Favorites for a specific user"""
        return self.get_queryset().filter(user=user)

    def favorites_for_model(self, model, user=None):
        """Returns Favorites for a specific model"""
        content_type = ContentType.objects.get_for_model(model)
        qs = self.get_queryset().filter(content_type=content_type).only("id")
        if user:
            qs = qs.filter(user=user)
        return qs

    def favorites_for_object(self, obj, user=None):
        """Returns Favorites for a specific object"""
        content_type = ContentType.objects.get_for_model(type(obj))
        qs = self.get_queryset().filter(content_type=content_type, object_id=obj.pk)
        if user:
            qs = qs.filter(user=user)

        return qs

    def favorite_for_user(self, obj, user):
        """Returns the favorite, if exists for obj by user"""
        content_type = ContentType.objects.get_for_model(type(obj))
        return self.get_queryset().get(content_type=content_type, object_id=obj.pk)


class InventoryOperationsManager(ActiveMixin, models.Manager):

    # override create method to set the inventory_quantity
    def create(self, *args, **kwargs):
        from ob_dj_store.core.stores.models._inventory import (
            Inventory,
            InventoryOperations,
        )

        # based on the operation type, set the inventory_quantity
        # get the store and the product variant in the kwargs
        store = kwargs.get("store")
        product_variant = kwargs.get("product_variant")
        # get the inventory_quantity from the product variant
        inventory = Inventory.objects.filter(
            store=store, variant=product_variant
        ).first()

        if inventory:
            inventory_quantity = inventory.quantity
            operation_quantity = kwargs.get("quantity")

            if (
                kwargs.get("type_of_operation")
                == InventoryOperations.Type_of_operation.STOCK_IN
            ):
                inventory_quantity += operation_quantity
            elif (
                kwargs.get("type_of_operation")
                == InventoryOperations.Type_of_operation.STOCK_OUT
            ):
                inventory_quantity -= operation_quantity

            inventory.quantity = inventory_quantity
            inventory.save()

        return super().create(*args, **kwargs)
