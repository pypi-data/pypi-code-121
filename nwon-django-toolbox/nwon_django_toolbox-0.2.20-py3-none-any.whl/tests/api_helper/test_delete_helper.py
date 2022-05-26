from typing import Optional

from django.db.models.base import Model

from nwon_django_toolbox.tests.api.api_test import ApiTest
from nwon_django_toolbox.url_helper import detail_url_for_model, list_url_for_model


def check_delete_basics(
    model: Model,
    authentication_token: Optional[str] = None,
):
    not_found_url = detail_url_for_model(model, "non-existing-id")
    detail_url = detail_url_for_model(model)

    api_test = ApiTest()

    api_test.delete_unauthorized(not_found_url)
    api_test.delete_unauthorized(detail_url)

    if authentication_token:
        api_test.set_bearer_token(authentication_token)
        api_test.delete_not_found(not_found_url)
        api_test.delete_successful(detail_url)
        api_test.get_not_found(detail_url)


def check_delete_not_allowed(
    model: Model,
    authentication_token: Optional[str] = None,
):
    api_test = ApiTest(token=authentication_token)

    detail_url = detail_url_for_model(model)
    list_url = list_url_for_model(model)

    api_test.delete_method_not_allowed(detail_url)
    api_test.delete_method_not_allowed(list_url)


__all__ = [
    "check_delete_basics",
    "check_delete_not_allowed",
]
