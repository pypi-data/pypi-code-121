from psu_base.classes.Finti import Finti
from psu_base.services import auth_service, utility_service, message_service
from psu_base.classes.Log import Log
from psu_authorize.classes.Application import Application
from psu_authorize.classes.Authority import Authority
from psu_authorize.classes.Permission import Permission

log = Log()
security_roles = "~security_officer"


def get_authorities():
    """
    Get a list of all defined WDT authorities
    """
    authorities = Authority.gather(Finti().get("wdt/v1/sso_proxy/manage/authorities"))
    return authorities


def get_all_applications():
    """
    Get all defined WDT custom web applications
    """
    log.trace()
    applications = []
    try:
        app_list = Finti().get("wdt/v1/sso_proxy/manage/applications")
        applications = Application.gather(app_list)
    except Exception as ee:
        log.error(f"Error getting applications: {str(ee)}")
    return applications


# For which apps can the current user manage permissions?
def get_manageable_applications():
    log.trace()

    # This gets called a lot.  Only do the processing once per request
    cached_response = utility_service.recall()
    if cached_response:
        return cached_response

    allowed_applications = []

    # Get application definitions
    all_applications = get_all_applications()

    # Is the current user a GLOBAL authorizer?
    if auth_service.has_authority(
        security_roles, utility_service.is_production(), True
    ):
        allowed_applications = all_applications
        # They may also assign global permissions
        allowed_applications.append(Application.global_app())

    # If not, iterate through permissions to get allowed apps
    else:
        # Get current user
        auth_object = auth_service.get_auth_object()
        username = auth_object.get_user().username
        # Only allow impersonation in non-prod
        if utility_service.is_production():
            username = auth_object.sso_user.username

        # Get all permissions (for all apps)
        user_permissions = Permission.gather(
            Finti().get(f"wdt/v1/sso_proxy/manage/permissions/all_apps/{username}")
        )

        # Get all authorized app codes
        auth_app_codes = []
        for pp in user_permissions:
            if pp.authority_code in security_roles:
                auth_app_codes.append(pp.app_code)
        # Gather app data for authorized apps
        for aa in all_applications:
            if aa.code in auth_app_codes:
                allowed_applications.append(aa)

    # Save for duration of request
    utility_service.store(allowed_applications)
    del all_applications

    return allowed_applications


def get_manageable_application_codes():
    """Same as above, but return only a list of the codes"""
    return [aa.code for aa in get_manageable_applications()]


def get_manageable_application_options():
    """Same as above, but return code and title (for use in select menu)"""
    return {aa.code: aa.title for aa in get_manageable_applications()}


def can_manage_global():
    return "GLOBAL" in get_manageable_application_codes()


def get_app_permissions(app_code):
    # Get all defined authorities
    all_authorities = get_authorities()
    all_authorities = sorted(all_authorities, key=lambda k: k.title)

    # Get all user permissions
    all_permissions = Permission.gather(
        Finti().get(f"wdt/v1/sso_proxy/manage/permissions/{app_code}")
    )

    # Sort by global or app-specific
    local_permissions = [
        pp for pp in all_permissions if pp.app_code == app_code
    ]
    # If the local (selected) app is "GLOBAL", then consider global permissions to be local
    if app_code == "GLOBAL":
        global_permissions = []
    else:
        global_permissions = [pp for pp in all_permissions if pp.app_code == "GLOBAL"]

    # Sort by direct or indirect access
    global_direct = [pp for pp in global_permissions if pp.via == "Direct Assignment"]
    global_indirect = [pp for pp in global_permissions if pp.via != "Direct Assignment"]
    local_direct = [pp for pp in local_permissions if pp.via == "Direct Assignment"]
    local_indirect = [pp for pp in local_permissions if pp.via != "Direct Assignment"]

    # Group global indirect accesses by assignment ID
    global_indirect_grouped = {}
    for pp in global_indirect:
        pid = pp.id
        if pid not in global_indirect_grouped:
            global_indirect_grouped[pid] = []
        global_indirect_grouped[pid].append(pp)

    # Assemble a final map of authorities, grouped into global and local, direct and indirect
    authority_map = {}
    for aa in all_authorities:
        this_map = {
            "code": aa.code,
            "title": aa.title,
            "description": aa.description,
            "global": {"direct": [], "indirect": []},
            "local": {"direct": [], "indirect": []},
        }
        for pp in global_direct:
            if pp.authority_code == aa.code:
                this_map["global"]["direct"].append(pp)
        for pp in global_indirect:
            if pp.authority_code == aa.code:
                this_map["global"]["indirect"].append(pp)

        for pp in local_direct:
            if pp.authority_code == aa.code:
                this_map["local"]["direct"].append(pp)
        for pp in local_indirect:
            if pp.authority_code == aa.code:
                this_map["local"]["indirect"].append(pp)

        # Add this map to the larger map
        authority_map[aa.code] = this_map

    response_map = {
        "authority_info": all_authorities,
        "authority_options": {aa.id: aa.title for aa in all_authorities},
        "granted_authorities": authority_map,
    }

    return response_map


def get_permission(permission_id):
    """Get details of one asigned permission"""
    log.trace([permission_id])
    pp = Finti().get(f"wdt/v1/sso_proxy/manage/permissions/{permission_id}")
    if pp:
        return Permission(pp)
    else:
        return None


def revoke_permission(permission_id):
    """Revoke one assigned permission"""
    log.trace([permission_id])
    response = Finti().delete(
        f"wdt/v1/sso_proxy/manage/permissions/{permission_id}", include_metadata=True
    )


def grant_permission(app_code, authority_id, grantees):
    """Grant permission to a grantee, or list of grantees (csv string or a list)"""
    log.trace([app_code, authority_id, grantees])
    new_permissions = []

    # Get grantees
    if type(grantees) is str:
        grantee_list = utility_service.csv_to_list(grantees)
    elif type(grantees) is list:
        grantee_list = grantees
    else:
        log.warn("No grantees were provided, or grantee list was invalid")
        return new_permissions

    # Iterate through grantees
    for grantee in grantee_list:
        try:
            response = Finti().post(
                f"/wdt/v1/sso_proxy/manage/permissions/{app_code}/{grantee}",
                payload={"authority_id": authority_id},
                include_metadata=True,
            )

            if response and response["result"] == "success":
                new_id = int(response["message"])
                if new_id:
                    new_permission = get_permission(new_id)
                    if new_permission:
                        new_permissions.append(new_permission)
                        continue
                log.error(
                    f"Permission assignment for {grantee} could not be verified: {response}"
                )
            else:
                log.error(f"Permission assignment for {grantee} failed: {response}")
        except Exception as ee:
            log.error(f"Error granting permission to {grantee}: {str(ee)}")

    # Notify user and log results
    num_new_permissions = len(new_permissions)
    log.info(
        f"Assigned {num_new_permissions} permission{'' if num_new_permissions == 1 else 's'} for {app_code}"
    )
    if num_new_permissions and num_new_permissions < 5:
        for pp in new_permissions:
            grantee = pp.username if pp.username else pp.via
            message_service.post_success(f"Permission granted to {grantee}")
    elif num_new_permissions:
        message_service.post_success(f"{num_new_permissions} new permissions granted")
    else:
        message_service.post_warning("No new permissions were granted")

    # Return a list of new permissions
    return new_permissions


def new_application(app_code, title):
    """Add a new application"""
    log.trace([app_code, title])
    applications = None

    if type(app_code) is not str:
        log.warn("No application title was provided, or title was invalid")
        return None
    try:
        response = Finti().post(
            f"/wdt/v1/sso_proxy/manage/applications/{app_code}",
            payload={"title": title},
            include_metadata=True,
        )
        if response and response["result"] == "success":
            new_id = int(response["message"])
            if new_id:
                applications = get_all_applications()
        else:
            log.error(f"{app_code} assignment failed: {response}")

    except Exception as ee:
        log.error(f"Error granting {app_code}: {str(ee)}")

    # Notify user and log results
    log.info(f"Application assigned")
    if applications:
        message_service.post_success(f"{app_code} application created")
    else:
        message_service.post_warning("No new applications were created")
    return applications


def new_authority(authority_code, title, description):
    """Add a new authority"""
    log.trace([authority_code, title, description])
    authorities = None

    if type(title) is not str:
        log.warn("No authority title was provided, or title was invalid")
        return None
    try:
        response = Finti().post(
            f"/wdt/v1/sso_proxy/manage/authorities/{authority_code}",
            payload={"title": title, "description": description},
            include_metadata=True,
        )
        if response and response["result"] == "success":
            new_id = int(response["message"])
            if new_id:
                authorities = get_authorities()

        else:
            log.error(f"Authority assignment for {title} failed: {response}")

    except Exception as ee:
        log.error(f"Error creating {title} authority: {str(ee)}")
        # Notify user and log results
    log.info(f"created an authority")
    if authorities:
        message_service.post_success(f"{title} authority is created")
    else:
        message_service.post_warning("No new authorities were created")
    return authorities


def delete_authority(authority_id):
    """Delete one assigned authority"""
    log.trace([authority_id])
    response = Finti().delete(
        f"/wdt/v1/sso_proxy/manage/authorities/{authority_id}", include_metadata=True
    )
    return response["result"]
