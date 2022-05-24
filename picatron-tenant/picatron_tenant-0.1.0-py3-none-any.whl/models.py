import uuid

from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction

from django_tenants import get_tenant_model
from django_tenants import app_settings


def slugify_function(content):
    translation_table = str.maketrans("ğĞıİöÖüÜşŞçÇ", "gGiIoOuUsScC")
    content = content.translate(translation_table)
    return slugify(content)


class AbstractBaseTenant(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    slug = models.CharField(max_length=100)

    domain_url = None
    domain_sub_folder = None

    class Meta:
        abstract = True

    @cached_property
    def is_main(self):
        return self.id == app_settings.MAIN_TENANT_ID


class AbstractTenant(AbstractBaseTenant):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("tenant")
        verbose_name_plural = _("tenants")
        abstract = True


class Tenant(AbstractTenant):

    class Meta(AbstractTenant.Meta):
        swappable = "TENANT_MODEL"


class Domain(models.Model):
    tenant = models.ForeignKey(app_settings.TENANT_MODEL, db_index=True, related_name='domains', on_delete=models.CASCADE)
    domain = models.CharField(max_length=253, unique=True, db_index=True)

    is_primary = models.BooleanField(default=True, db_index=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Get all other primary domains with the same tenant
        domain_list = self.__class__.objects.filter(tenant=self.tenant, is_primary=True).exclude(pk=self.pk)
        # If we have no primary domain yet, set as primary domain by default
        self.is_primary = self.is_primary or (not domain_list.exists())
        if self.is_primary:
            # Remove primary status of existing domains for tenant
            domain_list.update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.domain

    class Meta:
        abstract = True
        swappable = "DOMAIN_MODEL"


class RLSForeignKey(models.ForeignKey):
    rls_required = True


class TenantMixin(models.Model):
    tenant = RLSForeignKey(
        get_tenant_model(),
        on_delete=models.PROTECT,
        related_query_name='%(class)s',
    )

    class Meta:
        abstract = True

    def _do_insert(self, manager, using, fields, returning_fields, raw):
        modified_fields = [field for field in fields if not hasattr(field, 'rls_required') or not field.rls_required]
        return super(TenantMixin, self)._do_insert(manager, using, modified_fields, returning_fields, raw)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        modified_values = [value for value in values if not hasattr(value[0], 'rls_required') or not value[0].rls_required]
        return super(TenantMixin, self)._do_update(base_qs, using, pk_val, modified_values, update_fields, forced_update)
