import logging
from rest_framework.views import APIView
from django.contrib.auth import mixins, views as auth_views
from django.views import i18n, generic
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

class EnsurePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path in ["/", "/login"] or (request.path.startswith("/d-i/") and request.path != "/d-i/"):
            return

        if request.path in ["/profile"]:
            if not request.user.is_superuser:
                return auth_views.redirect_to_login(request.get_full_path())
            return

        if not hasattr(view_func, "view_class"):
            # Function-based view:
            # we require user to be an administrator,
            # except for Django admin and dashboard (we require staff)
            if view_func.__module__.startswith("django.contrib.admin.") or view_func.__module__.startswith("django_sql_dashboard.views"):
                if request.user.is_staff:
                    return
                return auth_views.redirect_to_login(request.get_full_path())
            elif not request.user.is_superuser:
                logger.warning("Function-based view %s: administrator required", ".".join([view_func.__module__, view_func.__name__]))
                return auth_views.redirect_to_login(request.get_full_path())
            return

        # Class-based view
        view = view_func.view_class

        if issubclass(view, (auth_views.LoginView, auth_views.LogoutView, generic.base.RedirectView)):
            # By defaut, accept non-authenticated users
            return

        if issubclass(view, (i18n.JavaScriptCatalog)):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("403 Forbidden") # do not redirect to login page (this is supposed to be accessed by javascript or as an API)
            return

        if issubclass(view, APIView):
            # Rest framework view: permission_classes should be configured globally
            # (REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES: rest_framework.permissions.IsAdminUser),
            # and overriden on a view-by-view basis when needed
            if not view.permission_classes:
                if not request.user.is_superuser:
                    logger.warning("No permission_classes for rest_framework view %s: administrator required", ".".join([view.__module__, view.__name__]))
                    return HttpResponseForbidden("403 Forbidden") # do not redirect to login page (this is supposed to be accessed by javascript or as an API)
            return

        # Other Django class-based view: if it does not explictly use AccessMixin,
        # we require user to be an administrator
        if not issubclass(view, mixins.AccessMixin):
            if not request.user.is_superuser:
                logger.warning("No AccessMixin for view %s: administrator required", ".".join([view.__module__, view.__name__]))
                return auth_views.redirect_to_login(request.get_full_path())
            return
