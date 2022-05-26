from cryptography.fernet import Fernet
from django import forms
from django.conf import settings
from django.db import models

__all__ = ["EncryptedTextField"]


class EncryptedTextField(models.TextField):
    """
    A text field that gets encrypted and decrypted using the django secret key
    """

    description = (
        "A text field that gets encrypted and decrypted using the django secret key"
    )

    fernet = Fernet(settings.FERNET_KEY.encode("utf-8"))

    def get_prep_value(self, value) -> str:
        return EncryptedTextField.fernet.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        return EncryptedTextField.fernet.decrypt(str.encode(value)).decode()

    def formfield(self, **kwargs):
        defaults = {"widget": forms.PasswordInput(render_value=True)}
        kwargs.update(defaults)

        return super().formfield(**kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
