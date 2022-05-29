from typing import Optional

from django.db.models import Model
from django.urls import reverse
from django.utils.html import format_html

from nwon_django_toolbox.settings import NWON_DJANGO_SETTINGS
from nwon_django_toolbox.url_helper.url_helper import base_name_from_model


def formatted_django_admin_link(model: Model, application: str = "tamoc") -> str:
    if application is None:
        raise Exception(
            "In order to use django_admin_link_for_model you need to set application_name in the NWON_DJANGO settings"
        )

    url = django_admin_link_for_model(model, application)
    return format_html("<a href='{url}'>{text}</a>", url=url, text=model.__str__())


def django_admin_link_for_model(
    model: Model,
    application: Optional[str] = NWON_DJANGO_SETTINGS.application_name,
) -> str:
    if application is None:
        raise Exception(
            "In order to use django_admin_link_for_model you need to set application_name in the NWON_DJANGO settings"
        )

    return reverse(
        f"admin:{application}_{base_name_from_model(model)}_change",
        args=(model.pk,),
    )


__all__ = [
    "formatted_django_admin_link",
    "django_admin_link_for_model",
]
