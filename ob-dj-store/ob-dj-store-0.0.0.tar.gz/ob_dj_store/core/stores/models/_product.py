from datetime import timedelta

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import (
    CategoryManager,
    ProductManager,
    ProductVariantManager,
)
from ob_dj_store.utils.helpers import product_media_upload_to
from ob_dj_store.utils.model import DjangoModelCleanMixin


class Category(DjangoModelCleanMixin, models.Model):
    """
    Represent categories where products can associate with
    """

    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=200, help_text=_("Name"))
    description = models.TextField(null=True, blank=True)
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.name}"


class ProductTag(models.Model):
    """
    ProductTag is look up table for indexing and filtering
    """

    name = models.CharField(max_length=500)
    text_color = models.CharField(
        default="#000000",
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Can you please provide a valid color hex !",
            ),
        ],
    )
    background_color = models.CharField(
        default="#000000",
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Can you please provide a valid color hex !",
            ),
        ],
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return f"Tag {self.name} (PK={self.pk})"


class Product(DjangoModelCleanMixin, models.Model):
    """
    Product is the main class that hold the basic info about the products
    """

    store = models.ForeignKey(
        "stores.store", on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200, help_text=_("Name"))
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=False)
    tags = models.ManyToManyField(ProductTag, related_name="products", blank=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return f"Product {self.name} (PK={self.pk})"


class AttributeChoice(DjangoModelCleanMixin, models.Model):
    """
    AttributeChoice represent a characteristic value for products
    """

    name = models.CharField(max_length=200, help_text=_("Name"))

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Attribute Choice")
        verbose_name_plural = _("Attribute Choices")

    def __str__(self):
        return f"Attribute Choice {self.name} (PK={self.pk})"


class Attribute(DjangoModelCleanMixin, models.Model):
    """
    Attribute represent a characteristic type for products
    """

    name = models.CharField(max_length=200, help_text=_("Name"))

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Attribute ")
        verbose_name_plural = _("Attributes")

    def __str__(self):
        return f"Attribute {self.name} (PK={self.pk})"


class ProductAttribute(DjangoModelCleanMixin, models.Model):
    """
    ProductAttribute represent a characteristic -attribute- with is choices -attribute_choices-
    """

    name = models.CharField(max_length=200, help_text=_("Name"))
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="product_attributes"
    )
    attribute_choices = models.ManyToManyField(
        AttributeChoice, related_name="product_attributes", blank=True
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")

    def __str__(self):
        return f"Product Attribute {self.name} (PK={self.pk})"


class ProductVariant(DjangoModelCleanMixin, models.Model):
    """
    Productvariant is an actual type of a unique product,Every product must have a minimum of one product variantion,
    A productvariant is defined with multiple characteristics stored in `product_attributes`
    """

    name = models.CharField(max_length=200, help_text=_("Name"))
    product = models.ForeignKey(
        Product, related_name="product_variants", on_delete=models.CASCADE
    )
    product_attributes = models.ManyToManyField(
        ProductAttribute, related_name="product_variants", blank=True
    )
    price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )
    quantity = models.PositiveIntegerField()
    preparation_time = models.DurationField(
        default=timedelta(minutes=0),
        help_text=_("Preparation time in minutes"),
    )
    sku = models.CharField(max_length=100, null=True, blank=True)
    is_deliverable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductVariantManager()

    class Meta:
        verbose_name = _("Product Variation")
        verbose_name_plural = _("Product Variations")

    def __str__(self):
        return f"Product Variation {self.name} (PK={self.pk})"


class ProductMedia(DjangoModelCleanMixin, models.Model):
    """
    Each Product can have many images to display, but only one primary
    """

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to=product_media_upload_to)
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_primary_image",
                fields=("product_id", "is_primary"),
                condition=models.Q(is_primary=True),
            ),
        ]
        ordering = ("order_value",)
        verbose_name = _("product media")
        verbose_name_plural = _("Product medias")
