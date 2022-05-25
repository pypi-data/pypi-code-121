from django.http import HttpResponse
from django.test import override_settings
from django.urls import path, reverse
from django.views.generic import View

from oauth2_provider.views.mixins import ScopedResourceMixin

from aleksis.core.util.auth_helpers import ClientProtectedResourceMixin


class TestViewClientProtectedResourceMixin(ScopedResourceMixin, ClientProtectedResourceMixin, View):
    required_scopes = ["write"]

    def get(self, request):
        return HttpResponse("OK")


urlpatterns = [
    path(
        "client_protected_resource_mixin_test/",
        TestViewClientProtectedResourceMixin.as_view(),
        name="client_protected_resource_mixin_test",
    ),
]
