from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from inviter2.models import OptOut


class RegistrationForm(UserCreationForm):
    """Slightly modified version of the standard Django UserCreationForm to
    enable the `is_active` field from the default of False."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Hide the UUID string
        self.initial['username'] = ''

    def save(self, *args, **kwargs):
        user = super(RegistrationForm, self).save(*args, **kwargs)
        user.is_active = True
        if kwargs.get('commit', True):
            user.save()
        return user


class OptOutForm(forms.ModelForm):
    """ Dummy form for opting out. """
    class Meta:
        model = User
        fields = ()

    def save(self):
        """ Delete the user object from the database and store the SHA1 hashed
        email address in the database to make sure this person does not receive
        any further invitation emails. """

        email = self.instance.email
        self.instance.delete()
        return OptOut.objects.create(email=email)
