from typing import List, Optional

from django.db.models.base import Model

from nwon_django_toolbox.tests.api.api_test import ApiTest
from nwon_django_toolbox.tests.helper.check_object_against_parameter import (
    check_object_against_parameter,
)
from nwon_django_toolbox.typings import RequestBodyFormat
from nwon_django_toolbox.url_helper import detail_url_for_model, list_url_for_model


def check_patch_basics(
    model: Model,
    authentication_token: Optional[str] = None,
):
    list_url = list_url_for_model(model)
    non_existing_detail_url = detail_url_for_model(model, "some-non-existing-id")
    detail_url = detail_url_for_model(model)

    api_test = ApiTest()

    api_test.patch_unauthorized(list_url, {})
    api_test.patch_unauthorized(non_existing_detail_url, {})
    api_test.patch_unauthorized(detail_url, {})

    if authentication_token:
        api_test.set_bearer_token(authentication_token)

        api_test.patch_method_not_allowed(list_url, {})
        api_test.patch_not_found(non_existing_detail_url, {})
        api_test.patch_successful(detail_url, {})


def check_patch_not_allowed(
    model: Model,
    authentication_token: Optional[str] = None,
):
    list_url = list_url_for_model(model)
    detail_url = detail_url_for_model(model)

    api_test = ApiTest(token=authentication_token)
    api_test.patch_method_not_allowed(list_url, {})
    api_test.patch_method_not_allowed(detail_url, {})


def check_patch_parameters_successful(
    model: Model,
    successful_parameters: List[dict],
    authentication_token: Optional[str] = None,
    body_format: RequestBodyFormat = RequestBodyFormat.Json,
):
    url = detail_url_for_model(model)
    api_test = ApiTest(token=authentication_token)

    # test a successful patch
    for successful_patch_parameter in successful_parameters:
        updated_object = api_test.patch_successful(
            url, successful_patch_parameter, body_format
        )
        check_object_against_parameter(updated_object, successful_patch_parameter)


def check_patch_parameters_failing(
    model: Model,
    failing_parameters: List[dict],
    authentication_token: Optional[str] = None,
    body_format: RequestBodyFormat = RequestBodyFormat.Json,
):
    url = detail_url_for_model(model)
    api_test = ApiTest(token=authentication_token)

    # test a failing patch
    for failing_patch_parameter in failing_parameters:
        api_test.patch_bad_request(url, failing_patch_parameter, body_format)


def check_patch_read_only_field(
    model: Model,
    successful_patch_parameter: dict,
    key: str,
    value,
    authentication_token: Optional[str] = None,
    body_format: RequestBodyFormat = RequestBodyFormat.Json,
):
    successful_patch_parameter[key] = value
    api_test = ApiTest(token=authentication_token)

    url = detail_url_for_model(model)
    updated_object = api_test.patch_successful(
        url, successful_patch_parameter, body_format
    )

    assert updated_object[key] != value


__all__ = [
    "check_patch_basics",
    "check_patch_not_allowed",
    "check_patch_parameters_failing",
    "check_patch_parameters_successful",
    "check_patch_read_only_field",
]
