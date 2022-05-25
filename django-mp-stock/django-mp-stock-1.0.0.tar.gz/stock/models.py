
from django.db import models
from django.utils.translation import ugettext_lazy as _

from stock import constants


class Stock(models.Model):

    stock = models.FloatField(_('Stock'), default=0)

    min_stock = models.FloatField(_('Minimum stock'), default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_stock = self.stock

    def add_stock(self, value):

        clean_value = self.clean_stock_value(value)

        self.stock += clean_value
        self._commit_stock()

    def subtract_stock(self, value):

        clean_value = self.clean_stock_value(value)

        if self.stock < clean_value:
            raise ValueError(_('Not enough stock items'))

        self.stock -= clean_value
        self._commit_stock()

    def clean_stock_value(self, value):

        try:
            value = float(value)
        except Exception:
            raise ValueError(_('Value should be float'))

        if value <= 0:
            raise ValueError(_('Value less then 0.1'))

        return value

    def _commit_stock(self):
        self.save(update_fields=['stock'])

    @property
    def has_stock(self):
        return self.stock > 0

    class Meta:
        abstract = True


class UnitType(models.Model):

    unit_type = models.CharField(
        _('Unit type'),
        max_length=100,
        choices=constants.UNIT_TYPES,
        default=constants.UNIT_TYPE_PCS)

    def format_qty(self, qty):
        return '{} {}'.format(qty, self.get_unit_type_display())

    class Meta:
        abstract = True
