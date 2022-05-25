
import barcode

from barcode.writer import ImageWriter

from django.db import models
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel


class BarCode(SingletonModel):

    next_code = models.IntegerField(
        _('Next bar code'), null=True, blank=True, default=1)

    def __str__(self):
        return 'Bar code'

    @classmethod
    def get_next_codes(cls, count):

        instance = cls.get_solo()

        next_codes = list(
            range(instance.next_code, instance.next_code + count))

        instance.next_code += count
        instance.save(update_fields=['next_code'])

        return [cls.format_code(code) for code in next_codes]

    @classmethod
    def get_next_code(cls):
        return cls.get_next_codes(1)[0]

    @classmethod
    def format_code(cls, code):
        ean = cls.get_ean("1{:011d}".format(code))
        return ean.get_fullcode()

    @classmethod
    def get_image(cls, code):
        return cls.get_ean(code).render(text=code)

    @classmethod
    def get_ean(cls, code):
        return barcode.get('ean', code, ImageWriter())

    class Meta:
        verbose_name = _('Bar code')
        verbose_name_plural = _('Bar codes')


class BarCodeField(models.CharField):

    def __init__(
            self,
            verbose_name=_('Bar code'),
            null=True,
            blank=True,
            max_length=255,
            db_index=True,
            **kwargs):
        super().__init__(
            verbose_name=verbose_name,
            null=null,
            blank=blank,
            max_length=max_length,
            db_index=db_index,
            **kwargs
        )

