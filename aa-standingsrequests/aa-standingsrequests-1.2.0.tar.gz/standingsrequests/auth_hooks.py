import logging

from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, ServicesHook, UrlHook

from . import __title__, urls
from .models import StandingRequest, StandingRevocation
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class StandingsRequestService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = "standingsrequests"
        self.urlpatterns = urlpatterns
        self.access_perm = StandingRequest.REQUEST_PERMISSION_NAME

    def delete_user(self, user, notify_user=False):
        logger.debug("Deleting user %s standings", user)
        StandingRequest.objects.filter(user=user).delete()

    def validate_user(self, user):
        logger.debug("Validating user %s standings", user)
        if not self.service_active_for_user(user):
            self.delete_user(user)

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)


@hooks.register("services_hook")
def register_service():
    return StandingsRequestService()


class StandingsRequestMenuItem(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(
            self,
            _(__title__),
            "fas fa-plus-square fa-fw grayiconecolor",
            "standingsrequests:index",
        )

    def render(self, request):
        if request.user.has_perm("standingsrequests.affect_standings"):
            app_count = (
                StandingRequest.objects.pending_requests().count()
                + StandingRevocation.objects.pending_requests().count()
            )
            self.count = app_count if app_count and app_count > 0 else None
        if request.user.has_perm(StandingRequest.REQUEST_PERMISSION_NAME):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return StandingsRequestMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "standingsrequests", r"^standingsrequests/")
