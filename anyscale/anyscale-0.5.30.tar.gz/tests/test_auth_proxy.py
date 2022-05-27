from http.cookies import SimpleCookie
from typing import Optional
from unittest.mock import Mock

import pytest

from anyscale.auth_proxy import authorize, index, make_auth_proxy_app


async def test_auth_token_redirect_serve():
    make_auth_proxy_app("mock_auth_token", None)
    mock_request = Mock(
        query={"token": "mock_auth_token", "redirect_to": None, "auth_only": None},
        headers={"Host": "serve-session-id.i.anyscaleuserdata-staging.com"},
    )

    resp = await index(mock_request)
    assert resp.status == 302
    assert resp.location == "https://serve-session-id.i.anyscaleuserdata-staging.com"

    expected_cookies = SimpleCookie()
    expected_cookies["anyscale-token"] = "mock_auth_token"
    expected_cookies["anyscale-token"]["path"] = "/"
    assert str(resp.cookies) == str(expected_cookies)


@pytest.mark.parametrize(
    "service",
    [
        "tensorboard",
        "dashboard",
        "grafana",
        "webterminal",
        "serve",
        "hosted_dashboard",
        "anyscaled",
        "metrics",
    ],
)
@pytest.mark.parametrize("auth_only", [True, None])
async def test_auth_token_redirect_services(service: str, auth_only: Optional[bool]):
    make_auth_proxy_app("mock_auth_token", None)
    mock_request = Mock(
        query={
            "token": "mock_auth_token",
            "redirect_to": service,
            "auth_only": auth_only,
        },
        headers={"Host": "session-id.i.anyscaleuserdata-staging.com"},
    )

    resp = await index(mock_request)
    if auth_only:
        assert resp.status == 200
    else:
        assert resp.status == 302

        redirect_path = {
            "tensorboard": "/tensorboard/",
            "grafana": "/grafana/",
            "dashboard": "/",
            "hosted_dashboard": "/metrics/redirect",
            "webterminal": "/webterminal/",
            "anyscaled": "/anyscaled/",
            "metrics": "/metrics",
            "autoscalermetrics": "/autoscalermetrics",
            "serve": "/serve",
        }
        assert resp.location == redirect_path[service]

    expected_cookies: SimpleCookie = SimpleCookie()
    expected_cookies["anyscale-token"] = "mock_auth_token"
    expected_cookies["anyscale-token"]["path"] = "/"
    if service == "webterminal":
        expected_cookies["anyscale-token"]["samesite"] = None
        expected_cookies["anyscale-token"]["secure"] = True
    assert str(resp.cookies) == str(expected_cookies)

    # Test redirect for user service urls
    make_auth_proxy_app("mock_auth_token", "mock_user_service_token")
    mock_request = Mock(
        query={
            "token": "mock_user_service_token",
            "redirect_to": "docs",
            "auth_only": None,
        },
        headers={"Host": "serve-session-id.i.anyscaleuserdata-staging.com"},
    )

    resp = await index(mock_request)
    assert resp.status == 302
    assert (
        resp.location == "https://serve-session-id.i.anyscaleuserdata-staging.com/docs"
    )
    expected_cookies_user_service: SimpleCookie = SimpleCookie()
    expected_cookies_user_service["anyscale-token"] = "mock_user_service_token"
    expected_cookies_user_service["anyscale-token"]["path"] = "/"
    assert str(resp.cookies) == str(expected_cookies_user_service)


@pytest.mark.parametrize(
    "mock_request",
    [
        Mock(cookies={"anyscale-token": "mock_auth_token"}),
        Mock(headers={"Authorization": "Bearer mock_auth_token"}),
        Mock(headers={"Authorization": "bearer mock_auth_token"}),
    ],
)
@pytest.mark.parametrize("use_token", ["access_token", "user_service_token"])
async def test_authorize_success(mock_request: Mock, use_token: str):
    mock_request.config_dict = {
        "auth_token": "mock_auth_token",
        "user_service_token": "mock_auth_token",
    }
    mock_request.query = {"use_token": use_token}
    make_auth_proxy_app("mock_auth_token", "mock_auth_token")

    resp = await authorize(mock_request)
    assert resp.status == 200


@pytest.mark.parametrize(
    "mock_request",
    [
        Mock(cookies={"anyscale-token": "mock_incorrect_auth_token"}),
        Mock(headers={"Authorization": "Bearer mock_incorrect_auth_token"}),
        Mock(headers={"Authorization": "bearer mock_incorrect_auth_token"}),
        Mock(),
    ],
)
@pytest.mark.parametrize("use_token", ["access_token", "user_service_token"])
async def test_authorize_failure(mock_request: Mock, use_token: str):
    mock_request.config_dict = {
        "auth_token": "mock_auth_token",
        "user_service_token": "mock_auth_token",
    }
    mock_request.query = {"use_token": use_token}
    make_auth_proxy_app("mock_auth_token", "mock_auth_token")

    resp = await authorize(mock_request)
    assert resp.status == 401
