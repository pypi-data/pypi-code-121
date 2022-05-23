from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from ob_dj_store.core.stores.models import Cart, ProductVariant
from ob_dj_store.core.stores.models._inventory import Inventory


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="create_customer_cart_handler",
)
def create_customer_cart_handler(sender, instance, created, **kwargs):
    if not created:
        return
    cart = Cart(customer=instance)
    cart.save()


# add receiver to ProductVariant to create inventory


@receiver(
    post_save,
    sender=ProductVariant,
    dispatch_uid="create_inventory_handler",
)
def create_inventory_handler(sender, instance, created, **kwargs):
    if not created:
        return
    Inventory.objects.create(
        variant=instance,
        quantity=instance.quantity,
        store=instance.product.store,
    )
