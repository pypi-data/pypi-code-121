
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Review(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='reviews',
        verbose_name=_('Owner'), null=True, blank=True,
        on_delete=models.SET_NULL)

    is_active = models.BooleanField(_('Is active'), default=False)

    name = models.CharField(_("Name"), max_length=255)

    rating = models.PositiveIntegerField(
        _('Rating'), default=5, choices=((x, str(x)) for x in range(1, 6)))

    date_created = models.DateTimeField(
        _('Date created'), auto_now_add=True, editable=False)

    text = models.TextField(_('Review'), max_length=1000, blank=False)

    photo = models.ImageField(
        _('Photo'), blank=True, null=True, upload_to='reviews')

    answer = models.TextField(_('Answer'), max_length=1000, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id', )
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
