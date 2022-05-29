from typing import Optional

from django.db.models.base import Model

from nwon_django_toolbox.tests.api.api_test import ApiTest
from nwon_django_toolbox.url_helper import (
    detail_url_for_model,
    list_url_for_model_class,
)


def check_get_basics(model: Model, authentication_token: Optional[str] = None):
    api_test = ApiTest()
    list_url = list_url_for_model_class(model.__class__)
    detail_url = detail_url_for_model(model, "some-non-existing-id")

    api_test.get_unauthorized(list_url)
    api_test.get_unauthorized(detail_url)

    if authentication_token:
        api_test.set_bearer_token(authentication_token)
        api_test.get_not_found(detail_url)

        url = detail_url_for_model(model)
        api_test.get_successful(url)


__all__ = [
    "check_get_basics",
]
