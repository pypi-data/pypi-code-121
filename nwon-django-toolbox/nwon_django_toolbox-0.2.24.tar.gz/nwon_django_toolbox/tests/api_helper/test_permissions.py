from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db.models import Model
from nwon_baseline.typings import AnyDict

from nwon_django_toolbox.tests.api import ApiTest
from nwon_django_toolbox.typings.permission_test_expectation import (
    LoginFunction,
    PermissionTestExpectation,
)
from nwon_django_toolbox.url_helper import detail_url_for_model, list_url_for_model

User = get_user_model()


def test_permissions(
    model: Model,
    expectations: List[PermissionTestExpectation],
    login_function: LoginFunction,
    post_parameter: Optional[AnyDict] = None,
    put_parameter: Optional[AnyDict] = None,
    patch_parameter: Optional[AnyDict] = None,
):
    for expectation in expectations:
        token = login_function(expectation.user, expectation.password)
        api_test = ApiTest(token)

        __test_get_list(api_test, model, expectation)
        __test_get_detail(api_test, model, expectation)
        __test_post(api_test, model, expectation, post_parameter)
        __test_put(api_test, model, expectation, put_parameter)
        __test_patch(api_test, model, expectation, patch_parameter)
        __test_delete(api_test, model, expectation)


def __test_get_list(
    api_test: ApiTest, model: Model, expectation: PermissionTestExpectation
):
    list_url = list_url_for_model(model)
    response = None
    if expectation.get_list_status_code:
        response = api_test.get_returns_status_code(
            list_url, expectation.get_list_status_code
        )
    elif expectation.get_list_return_number:
        response = api_test.get_successful(list_url)

    if expectation.get_list_return_number and response:
        assert len(response["results"]) == expectation.get_list_return_number


def __test_get_detail(
    api_test: ApiTest, model: Model, expectation: PermissionTestExpectation
):
    detail_url = detail_url_for_model(model)
    if expectation.get_detail_status_code:
        api_test.get_returns_status_code(detail_url, expectation.get_detail_status_code)


def __test_post(
    api_test: ApiTest,
    model: Model,
    expectation: PermissionTestExpectation,
    post_parameter: Optional[AnyDict],
):
    if expectation.create_status_code and post_parameter:
        list_url = list_url_for_model(model)
        api_test.post_returns_status_code(
            list_url, expectation.create_status_code, post_parameter
        )


def __test_put(
    api_test: ApiTest,
    model: Model,
    expectation: PermissionTestExpectation,
    put_parameter: Optional[AnyDict],
):
    if expectation.put_status_code and put_parameter:
        detail_url = detail_url_for_model(model)
        api_test.put_returns_status_code(
            detail_url, expectation.put_status_code, put_parameter
        )


def __test_patch(
    api_test: ApiTest,
    model: Model,
    expectation: PermissionTestExpectation,
    patch_parameter: Optional[AnyDict],
):
    if expectation.patch_status_code and patch_parameter:
        detail_url = detail_url_for_model(model)
        api_test.patch_returns_status_code(
            detail_url, expectation.patch_status_code, patch_parameter
        )


def __test_delete(
    api_test: ApiTest,
    model: Model,
    expectation: PermissionTestExpectation,
):
    detail_url = detail_url_for_model(model)
    if expectation.delete_status_code:
        api_test.delete_returns_status_code(detail_url, expectation.delete_status_code)
