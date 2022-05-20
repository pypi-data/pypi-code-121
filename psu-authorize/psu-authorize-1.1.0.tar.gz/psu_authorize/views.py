from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from psu_base.classes.Log import Log
from psu_base.services import error_service, message_service
from psu_base.decorators import require_authority
from psu_authorize.services import authorization_service


log = Log()

# ToDo: Error Handling/Messages

# Permission Checking
authorize_roles = "~SecurityOfficer"


@require_authority(authorize_roles)
def index(request):
    """
    Menu of authorized applications
    """
    log.trace()
    allowed_apps = authorization_service.get_manageable_applications()
    return render(request, "authorize_index.html", {"allowed_apps": allowed_apps})


@require_authority(authorize_roles)
def app(request, app_code):
    """
    Permissions for specified app
    """
    log.trace()
    # Gather app info
    allowed_apps = authorization_service.get_manageable_applications()
    app_info = None
    for aa in allowed_apps:
        if aa.code == app_code:
            app_info = aa

    # Make sure user can authorize for this app
    if app_code not in [aa.code for aa in allowed_apps]:
        message_service.post_error(
            f"You are not authorized to manage permissions for {app_code}"
        )
        return redirect("authorize:authorize_index")

    # Generate a list of application options for the user to select from when granting
    application_options = authorization_service.get_manageable_application_options()
    has_app_options = len(application_options) > 1

    # Get permissions for this app
    app_permissions = authorization_service.get_app_permissions(app_code)
    # Check whether user has global access
    global_access = authorization_service.can_manage_global()

    return render(
        request,
        "authorize/permissions/authorize_app.html",
        {
            "app_code": app_code,
            "app_info": app_info,
            "app_permissions": app_permissions,
            "application_options": application_options,
            "has_app_options": has_app_options,
            "global_access": global_access,
        },
    )


@require_authority(authorize_roles)
def revoke(request, permission_id):
    """
    Revoke one assigned permission
    """
    log.trace()
    try:
        permission_instance = authorization_service.get_permission(permission_id)
        if permission_instance:
            # Make sure user can authorize for this app
            allowed_apps = authorization_service.get_manageable_application_codes()
            if permission_instance.app_code in allowed_apps:
                authorization_service.revoke_permission(permission_id)
                message_service.post_success(
                    f"Permission #{permission_id} has been revoked"
                )
                return render(request, "authorize/permissions/_app_permission_rows.html", {})
            else:
                message_service.post_error(
                    f"You are not authorized to manage permissions for {permission_instance.app_code}"
                )
        else:
            message_service.post_error(f"Unable to find permission #{permission_id}")
    except Exception as ee:
        error_service.unexpected_error("Unable to revoke permission", ee)
    return HttpResponseForbidden()


@require_authority(authorize_roles)
def grant(request):
    """
    Grant one authority to one or more users
    """
    log.trace()
    try:
        app_code = request.POST.get("app_code")
        authority_id = request.POST.get("authority_id")
        grantee = request.POST.get("grantee")
        allowed_apps = authorization_service.get_manageable_application_codes()
        if app_code in allowed_apps:
            new_permissions = authorization_service.grant_permission(
                app_code, authority_id, grantee
            )
            authority_code = (
                new_permissions[0].authority_code
                if new_permissions and len(new_permissions) > 0
                else None
            )
            return render(
                request,
                "authorize/permissions/_app_permission_rows.html",
                {"permissions": {authority_code: {"new": new_permissions}}.items()},
            )
        else:
            message_service.post_error(
                f"You are not authorized to grant permissions for {app_code}"
            )

    except Exception as ee:
        error_service.unexpected_error("Unable to grant permission", ee)
    return HttpResponseForbidden()


@require_authority(authorize_roles)
def manage_apps(request):
    """
    List all the applications
    """
    if not authorization_service.can_manage_global():
        message_service.post_error(
            "You must have global authorization authority to manage application definitions"
        )
        return redirect("authorize:authorize_index")

    apps = authorization_service.get_all_applications()
    return render(request, "manage_new_app.html", {"apps": apps})


@require_authority(authorize_roles)
def new_apps(request):
    """
    Create new application
    """
    log.trace()
    try:
        if not authorization_service.can_manage_global():
            message_service.post_error(
                "You must have global authorization authority to create application definitions"
            )
            return HttpResponseForbidden()

        app_code = request.POST.get("app_code")
        if not app_code:
            message_service.post_error("App code is required.")
            return HttpResponseForbidden()
        elif len(app_code) > 15:
            message_service.post_error("Max app code length is 15 characters.")
            return HttpResponseForbidden()

        title = request.POST.get("app_title")
        if not title:
            message_service.post_error("App title is required.")
            return HttpResponseForbidden()
        elif len(title) > 30:
            message_service.post_error("Max title length is 30 characters.")
            return HttpResponseForbidden()

        apps = authorization_service.new_application(app_code, title)
        for aa in apps:
            if app_code.upper() == aa.code:
                return render(request, "application_rows.html", {"apps": [aa]})

    except Exception as ee:
        error_service.unexpected_error("Unable to create application", ee)
    return HttpResponseForbidden()


@require_authority(authorize_roles)
def manage_authorities(request):
    """
    List all the authorities
    """
    authorities = authorization_service.get_authorities()
    return render(
        request,
        "new_authority.html",
        {
            "authorities": authorities,
            "global_access": authorization_service.can_manage_global(),
        },
    )


@require_authority(authorize_roles)
def new_authority(request):
    """
    Create new authority
    """
    log.trace()
    try:
        authority_code = request.POST.get("authority_code")
        title = request.POST.get("title")
        description = request.POST.get("description")
        authorities = authorization_service.new_authority(
            authority_code, title, description
        )
        for auth in authorities:
            if authority_code == auth.code:
                return render(
                    request,
                    "authorities_rows.html",
                    {
                        "authorities": [auth],
                        "global_access": authorization_service.can_manage_global(),
                    },
                )

    except Exception as ee:
        error_service.unexpected_error("Unable to create authority", ee)
    return HttpResponseForbidden()


@require_authority(authorize_roles)
def delete_authority(request, authority_id):
    """
    Delete an authority
    """
    log.trace()
    try:
        if not authorization_service.can_manage_global():
            message_service.post_error(
                "You must have global authorization to delete authority definitions, which may affect other applications"
            )
            return redirect("authorize_index")

        response = authorization_service.delete_authority(authority_id)
        if response == "success":
            message_service.post_success(f"Authority #{authority_id} has been deleted")
            return render(request, "authorities_rows.html", {})
        else:
            message_service.post_success(f"authority is not deleted")

    except Exception as ee:
        error_service.unexpected_error("Unable to delete authority", ee)

    return HttpResponseForbidden()
