from hashlib import md5

from Cryptodome.PublicKey import RSA
from django.db import models
from django.utils.translation import ugettext_lazy as _


class RSAKey(models.Model):

    priv_key = models.TextField(
        verbose_name=_(u'Key'), unique=True,
        help_text=_(u'Paste your private RSA Key here.'))

    class Meta:
        verbose_name = _(u'RSA Key')
        verbose_name_plural = _(u'RSA Keys')

    def __str__(self):
        return u'{0}'.format(self.kid)

    def __unicode__(self):
        return self.__str__()

    @property
    def kid(self):
        if not self.priv_key:
            return ''

        return u'{0}'.format(md5(self.priv_key.encode('utf-8')).hexdigest())

    @property
    def pub_key(self):
        if not self.priv_key:
            return ''

        _pub_key = RSA.importKey(self.priv_key).publickey()
        return _pub_key.export_key().decode('utf-8')
