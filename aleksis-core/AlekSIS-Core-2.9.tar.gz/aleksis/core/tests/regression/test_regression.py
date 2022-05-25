import base64

from django.contrib.auth import get_user_model

import pytest

from aleksis.core.models import Group, OAuthApplication, Person

pytestmark = pytest.mark.django_db
from django.http import HttpResponse
from django.test import override_settings
from django.urls import path, reverse
from django.views.generic import View


def test_all_settigns_registered():
    """Tests for regressions of preferences not being registered.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/592
    """

    from dynamic_preferences.types import BasePreferenceType

    from aleksis.core import preferences
    from aleksis.core.preferences import person_preferences_registry, site_preferences_registry

    for obj in preferences.__dict__.values():
        if not isinstance(obj, BasePreferenceType):
            continue

        in_site_reg = site_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        in_person_reg = (
            person_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        )

        assert in_site_reg != in_person_reg


def test_custom_managers_return_correct_qs():
    """Tests that custom managers' get_queryset methods return the expected qs.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/594
    """

    from aleksis.core import managers

    def _check_get_queryset(Manager, QuerySet):
        assert isinstance(Manager.from_queryset(QuerySet)().get_queryset(), QuerySet)

    _check_get_queryset(managers.GroupManager, managers.GroupQuerySet)


def test_reassign_user_to_person():
    """Tests that on re-assigning a user, groups are correctly synced.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/628
    """

    User = get_user_model()

    group1 = Group.objects.create(name="Group 1")
    group2 = Group.objects.create(name="Group 2")

    user1 = User.objects.create(username="user1")
    user2 = User.objects.create(username="user2")

    person1 = Person.objects.create(first_name="Person", last_name="1", user=user1)
    person2 = Person.objects.create(first_name="Person", last_name="2", user=user2)

    person1.member_of.set([group1])
    person2.member_of.set([group2])

    assert user1.groups.count() == 1
    assert user2.groups.count() == 1
    assert user1.groups.first().name == "Group 1"
    assert user2.groups.first().name == "Group 2"

    person1.user = None
    person1.save()
    assert user1.groups.count() == 0

    person2.user = user1
    person2.save()
    person1.user = user2
    person1.save()

    assert user1.groups.count() == 1
    assert user2.groups.count() == 1
    assert user1.groups.first().name == "Group 2"
    assert user2.groups.first().name == "Group 1"


@override_settings(ROOT_URLCONF="aleksis.core.tests.regression.view_oauth")
def test_no_access_oauth2_client_credentials_without_allowed_scopes(client):
    """Tests that ClientProtectedResourceMixin doesn't allow access if no allowed scopes are set.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/688
    """

    wrong_application = OAuthApplication.objects.create(
        name="Test Application",
        allowed_scopes=[],
        authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
        client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
        redirect_uris=["http://localhost:8000/"],
    )
    wrong_application_2 = OAuthApplication.objects.create(
        name="Test Application",
        allowed_scopes=["read"],
        authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
        client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
        redirect_uris=["http://localhost:8000/"],
    )
    correct_application = OAuthApplication.objects.create(
        name="Test Application",
        allowed_scopes=["write"],
        authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
        client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
        redirect_uris=["http://localhost:8000/"],
    )

    url = reverse("client_protected_resource_mixin_test")
    auth_header = (
        "Basic "
        + base64.b64encode(
            f"{wrong_application.client_id}:{wrong_application.client_secret}".encode()
        ).decode()
    )
    r = client.get(url, HTTP_AUTHORIZATION=auth_header)
    assert r.status_code == 403

    auth_header = (
        "Basic "
        + base64.b64encode(
            f"{wrong_application_2.client_id}:{wrong_application_2.client_secret}".encode()
        ).decode()
    )
    r = client.get(url, HTTP_AUTHORIZATION=auth_header)
    assert r.status_code == 403

    auth_header = (
        "Basic "
        + base64.b64encode(
            f"{correct_application.client_id}:{correct_application.client_secret}".encode()
        ).decode()
    )
    r = client.get(url, HTTP_AUTHORIZATION=auth_header)
    assert r.status_code == 200
