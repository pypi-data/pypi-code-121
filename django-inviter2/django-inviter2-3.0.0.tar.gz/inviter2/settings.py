from django.conf import settings
from functools import partial

setting = partial(getattr, settings)

NAMESPACE = setting('INVITER_NAMESPACE', 'inviter2')

FROM_EMAIL = setting('INVITER_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

FORM = setting('INVITER_FORM', 'inviter2.forms.RegistrationForm')
FORM_USER_KWARG = setting('INVITER_FORM_USER_KWARG', 'instance')
FORM_TEMPLATE = setting('INVITER_FORM_TEMPLATE', 'inviter2/register.html')

DONE_TEMPLATE = setting('INVITER_DONE_TEMPLATE', 'inviter2/done.html')

OPTOUT_TEMPLATE = setting('INVITER_OPTOUT_TEMPLATE', 'inviter2/opt-out.html')
OPTOUT_DONE_TEMPLATE = setting(
    'INVITER_OPTOUT_DONE_TEMPLATE', 'inviter2/opt-out-done.html'
)

TOKEN_GENERATOR = setting(
    'INVITER_TOKEN_GENERATOR', 'inviter2.tokens.generator'
)

REDIRECT_URL = setting('INVITER_REDIRECT', '{}:done'.format(NAMESPACE))
