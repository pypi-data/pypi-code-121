
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Manager(models.Model):

    name = models.CharField(_('Manager name'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Manager')
        verbose_name_plural = _('Managers')


class ManagerField(models.ForeignKey):

    def __init__(
            self,
            to=Manager,
            verbose_name=_('Manager'),
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
