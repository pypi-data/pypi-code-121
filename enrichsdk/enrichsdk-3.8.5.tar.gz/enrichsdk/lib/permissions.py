def has_permissions(user, orgname, role=None):
    """
    Check whether user has permissions
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    orgroles = list(user.org_role_users.all())

    # Filter out all other organizations
    orgroles = [o for o in orgroles if o.org.name == orgname]

    # For the specific organization
    roles = [o.name for o in orgroles]

    if ("admin" in roles) or (role is not None and role in roles):
        return True

    # Denied
    return False
