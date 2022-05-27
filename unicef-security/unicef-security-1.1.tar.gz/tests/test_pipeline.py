from social_django.utils import load_backend, load_strategy

import pytest

from unicef_security.pipeline import create_unicef_user, get_username, social_details


@pytest.fixture()
def strategy():
    return load_strategy()


@pytest.fixture()
def backend(strategy):
    return load_backend(strategy=strategy, name='unicef-azuread-b2c-oauth2', redirect_uri='/')


@pytest.fixture()
def response(auth_user):
    return {
        'id_token': 'token',
        'token_type': 'Bearer',
        'not_before': 1607541825,
        'id_token_expires_in': 3600,
        'profile_info': 'profile_info',
        'scope': 'openid',
        'access_token': 'access_token',
        'exp': 1607545425,
        'nbf': 1607541825,
        'ver': '1.0',
        'iss': 'https://tenant.b2clogin.com/1234567890/v2.0/',
        'sub': 'abcdefgh', 'aud': 'abcdefgh',
        'acr': 'b2c_1a_unicef_social_signup_signin',
        'iat': 1607541825,
        'auth_time': 1607541824,
        'given_name': 'Given',
        'family_name': 'Family',
        'name': 'Given Family',
        'idp': 'UNICEF Azure AD',
        'email': auth_user.email
    }


@pytest.fixture()
def details(auth_user):
    return {
        'username': 'Given Family',
        'email': auth_user.email,
        'fullname': 'Given Family',
        'first_name': 'Given',
        'last_name': 'Family',
        'idp': 'UNICEF Azure AD'
    }


@pytest.mark.django_db
def test_social_details(auth_user, backend, details, response):
    return_dict = social_details(backend, details, response)
    assert 'idp' in return_dict['details']
    assert return_dict['details']['email'] == auth_user.email


@pytest.mark.django_db
def test_get_username(strategy, backend, details, auth_user):
    result_dict = get_username(strategy, details, backend, user=auth_user)
    assert 'username' in result_dict
    assert result_dict['username'] == auth_user.email


@pytest.mark.django_db
def test_create_unicef_user_ok(strategy, details, backend):
    result_dict = create_unicef_user(strategy, details, backend)
    assert result_dict['is_new']
    assert result_dict['user']


@pytest.mark.django_db
def test_create_unicef_user_ko(strategy, details, backend):
    details['email'] = 'test_undeliverable@example.com'
    result_dict = create_unicef_user(strategy, details, backend)
    assert not result_dict


@pytest.mark.django_db
def test_create_unicef_user_existing(strategy, details, backend):
    result_dict = create_unicef_user(strategy, details, backend, 1)
    assert 'is_new' in result_dict
    assert not result_dict['is_new']
