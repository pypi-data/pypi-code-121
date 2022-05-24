from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from custom_url.models import CustomUrl


class CustomUrlForm(forms.ModelForm):
    url = forms.RegexField(
        label=_('URL'),
        max_length=100,
        regex=r"^[-\w/\.~]+$",
        help_text=_('Example: “/cv/”. Make sure to have leading and trailing slashes.'),
        error_messages={
            "invalid": _('This value must be a valid URL path.'),
        },
    )

    class Meta:
        model = CustomUrl
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self._trailing_slash_required():
            self.fields['url'].help_text = _('Example: “/cv”. Make sure to have a leading slash.')

    def _trailing_slash_required(self):
        return (settings.APPEND_SLASH and 'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE)

    def clean_url(self):
        url = self.cleaned_data['url']

        if not url.startswith('/'):
            raise ValidationError(_('URL is missing a leading slash.'), code='missing_leading_slash')
        if self._trailing_slash_required() and not url.endswith('/'):
            raise ValidationError(_('URL is missing a trailing slash.'), code='missing_trailing_slash')
        return url