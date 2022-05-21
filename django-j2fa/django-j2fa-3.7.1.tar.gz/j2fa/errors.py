from django.core.exceptions import ValidationError


class TwoFactorAuthError(ValidationError):
    pass
