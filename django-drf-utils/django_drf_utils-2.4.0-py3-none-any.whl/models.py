from django.core import validators
from django.db import models


class CreatedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


def NameField(**kwargs):
    unique = kwargs.pop("unique", True)
    return models.CharField(
        max_length=512,
        unique=unique,
        validators=(
            validators.RegexValidator(
                regex=r"^[a-zA-Z0-9\- ()ßàÀéÉèÈäÄëËïÏöÖüÜçÇâÂêÊîÎôÔûÛ']*$",
                message="Allowed characters: "
                """"a-z", "A-Z", "0-9", "-", "(", ")", "'", """
                "spaces and diacritics.",
            ),
        ),
        **kwargs,
    )


def CodeField(lower: bool = True, **kwargs):
    unique = kwargs.pop("unique", True)
    char_set = "a-z" if lower else "A-Z"
    return models.CharField(
        max_length=32,
        unique=unique,
        validators=(
            validators.RegexValidator(
                regex=rf"^[{char_set}0-9_]*$",
                message=f'Allowed characters: "{char_set}", "0-9", "_"',
            ),
        ),
        **kwargs,
    )


def EnumField(choices, **kwargs):
    return models.CharField(
        max_length=max((len(key) for key, label_ in choices)), choices=choices, **kwargs
    )
