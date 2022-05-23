from django.contrib.auth import get_user_model

from django_registration.forms import RegistrationForm
from djangoldp_account.models import LDPUser


def _get_user_form_fields():
    '''Gets the fields required for the form from settings, or returns default'''
    from django.conf import settings
    return getattr(settings, 'REGISTRATION_FIELDS', ('username', 'email', 'password1', 'password2'))


class LDPUserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = get_user_model()
        fields = _get_user_form_fields()
