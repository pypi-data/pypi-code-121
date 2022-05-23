from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import CartItemManager, CartManager


class Cart(models.Model):
    customer = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="cart",
        primary_key=True,
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CartManager()

    class Meta:
        verbose_name_plural = _("Carts")
        verbose_name = _("Cart")

    @property
    def total_price(self) -> Decimal:
        total_price = Decimal(0)
        for item in self.items.all():
            total_price += item.total_price
        return total_price

    def __str__(self):
        return f"Cart - {self.customer.email} with total price {self.total_price}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_variant = models.ForeignKey(
        "stores.ProductVariant", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CartItemManager()

    class Meta:
        verbose_name_plural = _("Cart Items")
        verbose_name = _("Cart Item")

    @property
    def unit_price(self) -> Decimal:
        return self.product_variant.price

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

    def __str__(self):
        return f"CartItem - {self.quantity} {self.product_variant.name}"
