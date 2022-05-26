
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Customer(models.Model):

    name = models.CharField(_('Customer name'), max_length=255)

    phone = models.CharField(_('Phone'), max_length=255, blank=True)

    vin = models.CharField(_('VIN code'), max_length=17, blank=True)

    discount = models.PositiveIntegerField(
        verbose_name=_('Discount, %'),
        default=0)

    def __str__(self):
        result = self.name

        if self.phone:
            result += ' / ' + self.phone

        return result

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class CustomerField(models.ForeignKey):

    def __init__(
            self,
            to=Customer,
            verbose_name=_('Customer'),
            blank=True,
            null=True,
            on_delete=models.PROTECT,
            **kwargs):

        super().__init__(
            to=to,
            verbose_name=verbose_name,
            blank=blank,
            null=null,
            on_delete=on_delete,
            **kwargs)
