from functools import wraps

from esi.decorators import _check_callback
from esi.models import Token
from esi.views import select_token, sso_redirect

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from . import __title__
from .models import StandingRequest

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def token_required_by_state(new=False):
    """
    Decorator for views which supplies a single,
    user-selected token for the view to process.
    No scopes can be provided instead scopes are selected
    from the scopes that are set as
    required for a specific state in the settings.
    param: new if a new token should be aquired
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            scopes = ""
            if request.user.profile.state is not None:
                scopes = " ".join(
                    StandingRequest.get_required_scopes_for_state(
                        request.user.profile.state.name
                    )
                )

            # if we're coming back from SSO for a new token, return it
            token = _check_callback(request)
            if token and new:
                logger.debug(
                    "Got new token from %s session %s. Returning to view.",
                    request.user,
                    request.session.session_key[:5],
                )
                return view_func(request, token, *args, **kwargs)

            # if we're selecting a token, return it
            if request.method == "POST":
                if request.POST.get("_add", False):
                    logger.debug(
                        "%s has selected to add new token. Redirecting to SSO.",
                        request.user,
                    )
                    # user has selected to add a new token
                    return sso_redirect(request, scopes=scopes)

                token_pk = request.POST.get("_token", None)
                if token_pk:
                    token_pk = int(token_pk)
                    logger.debug("%s has selected token %d", request.user, token_pk)
                    try:
                        token = Token.objects.get(pk=token_pk)
                        # ensure token belongs to this user and has required scopes
                        if (
                            (token.user and token.user == request.user)
                            or not token.user
                        ) and Token.objects.filter(pk=token_pk).require_scopes(
                            scopes
                        ).require_valid().exists():
                            logger.debug(
                                "Selected token fulfills requirements of view."
                                " Returning."
                            )
                            return view_func(request, token, *args, **kwargs)
                    except Token.DoesNotExist:
                        logger.debug("Token %d not found.", token_pk)

            if not new:
                # present the user with token choices
                tokens = (
                    Token.objects.filter(user__pk=request.user.pk)
                    .require_scopes(scopes)
                    .require_valid()
                )
                if tokens.exists():
                    logger.debug(
                        "Returning list of available tokens for %s.", request.user
                    )
                    return select_token(request, scopes=scopes, new=new)
                else:
                    logger.debug(
                        "No tokens found for %s session %s with scopes %s",
                        request.user,
                        request.session.session_key[:5],
                        scopes,
                    )

            # prompt the user to add a new token
            logger.debug(
                "Redirecting %s session %s to SSO.",
                request.user,
                request.session.session_key[:5],
            )
            return sso_redirect(request, scopes=scopes)

        return _wrapped_view

    return decorator
