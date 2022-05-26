import copy
from typing import List, Optional, Type

from django.db.models.base import Model

from nwon_django_toolbox.tests.api.api_test import ApiTest
from nwon_django_toolbox.tests.helper.check_object_against_parameter import (
    check_object_against_parameter,
)
from nwon_django_toolbox.typings import RequestBodyFormat
from nwon_django_toolbox.url_helper import (
    detail_url_for_model,
    detail_url_for_model_class,
    list_url_for_model_class,
)


def check_post_basics(
    model_class: Type[Model],
    authentication_token: Optional[str] = None,
    body_format=RequestBodyFormat.Json,
):
    api_test = ApiTest()
    url = detail_url_for_model_class(model_class, "some-non-existing-id")

    # post on detail url is not allowed
    api_test.post_unauthorized(url, {}, body_format)

    if authentication_token:
        api_test.set_bearer_token(authentication_token)
        api_test.post_method_not_allowed(url, {}, body_format)


def check_post_not_allowed(
    model_class: Type[Model],
    authentication_token: Optional[str] = None,
):
    list_url = list_url_for_model_class(model_class)

    api_test = ApiTest(token=authentication_token)
    api_test.post_method_not_allowed(list_url, {})


def check_post_parameters_successful(
    model_class: Type[Model],
    successful_parameters: List[dict],
    authentication_token: Optional[str] = None,
    body_format=RequestBodyFormat.Json,
):
    list_url = list_url_for_model_class(model_class)
    api_test = ApiTest(token=authentication_token)

    for successful_parameter in successful_parameters:
        # test creation of object
        created_object = api_test.post_create_successful(
            list_url, successful_parameter, body_format=body_format
        )
        check_object_against_parameter(created_object, successful_parameter)

        # get object via get
        created_objet = model_class.objects.get(pk=created_object["id"])
        url = detail_url_for_model(created_objet)
        object_to_check = api_test.get_successful(url)
        check_object_against_parameter(object_to_check, successful_parameter)


def check_post_parameters_required(
    model_class: Type[Model],
    successful_parameter: dict,
    required_keys: List[str],
    authentication_token: Optional[str] = None,
    body_format=RequestBodyFormat.Json,
):
    list_url = list_url_for_model_class(model_class)
    api_test = ApiTest(token=authentication_token)

    # make sure that parameter are working
    api_test.post_create_successful(
        list_url, successful_parameter, body_format=body_format
    )

    for key in required_keys:
        parameter = copy.deepcopy(successful_parameter)
        parameter.pop(key)
        api_test.post_bad_request(list_url, parameter, body_format=body_format)


def check_post_parameters_not_required(
    model_class: Type[Model],
    successful_parameter: dict,
    required_keys: List[str],
    authentication_token: Optional[str] = None,
    body_format=RequestBodyFormat.Json,
):
    list_url = list_url_for_model_class(model_class)
    api_test = ApiTest(token=authentication_token)

    # make sure that parameter are working
    api_test.post_create_successful(
        list_url, successful_parameter, body_format=body_format
    )

    for key in required_keys:
        parameter = copy.deepcopy(successful_parameter)
        parameter.pop(key)
        api_test.post_create_successful(list_url, parameter, body_format=body_format)


def check_post_parameters_failing(
    model_class: Type[Model],
    failing_parameters: List[dict],
    authentication_token: Optional[str] = None,
    body_format=RequestBodyFormat.Json,
):
    list_url = list_url_for_model_class(model_class)
    api_test = ApiTest(token=authentication_token)

    for failing_parameter in failing_parameters:
        api_test.post_bad_request(list_url, failing_parameter, body_format=body_format)


def check_post_read_only_field(
    model_class: Type[Model],
    successful_post_parameter: dict,
    key: str,
    value,
    authentication_token: Optional[str] = None,
    body_format=RequestBodyFormat.Json,
):
    successful_post_parameter[key] = value

    list_url = list_url_for_model_class(model_class)
    api_test = ApiTest(token=authentication_token)

    created_object = api_test.post_create_successful(
        list_url, successful_post_parameter, body_format=body_format
    )

    # check whether read only key was set
    assert created_object[key] != value


__all__ = [
    "check_post_basics",
    "check_post_not_allowed",
    "check_post_parameters_failing",
    "check_post_parameters_successful",
    "check_post_read_only_field",
    "check_post_parameters_not_required",
]
