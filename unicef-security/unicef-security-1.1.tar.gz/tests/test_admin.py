from django.urls import reverse


def test_changelist(django_app, admin_user):
    url = reverse("admin:demo_user_changelist")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200
