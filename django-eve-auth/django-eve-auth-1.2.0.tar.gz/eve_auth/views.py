import logging

from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from esi.decorators import token_required
from esi.models import Token

from . import app_settings

logger = logging.getLogger(__name__)


@token_required(new=True, scopes=app_settings.EVE_AUTH_LOGIN_SCOPES)
def login(request, token: Token):
    """Login user with authorization from EVE SSO.

    GET parameters:
        - next: View will redirect to the given URL after after successful login, instead of the default `LOGIN_REDIRECT_URL`
    """
    next_page_url = request.GET.get("next")
    user = auth.authenticate(token=token)
    if user:
        token.user = user
        if (
            Token.objects.exclude(pk=token.pk)
            .equivalent_to(token)
            .require_valid()
            .exists()
        ):
            token.delete()
        else:
            token.save()
        if user.is_active:
            auth.login(request, user)
            logger.info("User %s has logged in.", user)
            return (
                redirect(next_page_url)
                if next_page_url
                else redirect(settings.LOGIN_REDIRECT_URL)
            )
        else:
            logger.info("User %s is inactive and therefore not allowed to login.", user)
            messages.warning(
                request, _("User %s has been banned from this website.", user)
            )
    else:
        logger.warning(
            "User authentication for character %s failed.", token.character_name
        )
        messages.error(
            request, _("Unable to authenticate character %s.", token.character_name)
        )
    return redirect(settings.LOGIN_URL)


def logout(request):
    """Logout current user.

    GET parameters:
        - next: View will redirect to the given URL after after successful logout, instead of the default `LOGIN_URL`
    """
    logger.info("Logging out user %s", request.user)
    auth.logout(request)
    next_page_url = request.GET.get("next")
    return redirect(next_page_url) if next_page_url else redirect(settings.LOGIN_URL)
