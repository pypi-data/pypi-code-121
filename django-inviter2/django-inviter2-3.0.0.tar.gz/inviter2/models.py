from __future__ import unicode_literals

from django.db import models
import hashlib


class OptOutManager(models.Manager):
    def _hash_email(self, email):
        email_bytes = email.encode('utf-8')
        return hashlib.sha1(email_bytes).hexdigest()

    def is_blocked(self, email=None):
        """ Check if a given email address is on the block list. """
        return self.filter(hash=self._hash_email(email)).count() > 0

    def create(self, email=None):
        """ Create an opt out. """
        return super(OptOutManager, self).create(hash=self._hash_email(email))


class OptOut(models.Model):
    """ Opt-out email addresses are stored as SHA1 hashes to make sure we don't
    accidentally collect any more data once a person signalled they're not
    interested in receiving any more invitation emails from us. """
    hash = models.CharField(max_length=255)

    objects = OptOutManager()

    def __unicode__(self):
        return self.hash



