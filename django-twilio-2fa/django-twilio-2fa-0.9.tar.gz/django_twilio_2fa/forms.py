from django import forms
from .utils import verify_phone_number


__all__ = [
    "Twilio2FARegistrationForm", "Twilio2FAVerifyForm",
]


class Twilio2FARegistrationForm(forms.Form):
    phone_number = forms.CharField()

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]
        transtab = str.maketrans("", "", "()-. _")
        phone.translate(transtab)

        verify_phone_number(phone, do_lookup=True)

        return phone


class Twilio2FAVerifyForm(forms.Form):
    token = forms.CharField(
        required=True
    )
