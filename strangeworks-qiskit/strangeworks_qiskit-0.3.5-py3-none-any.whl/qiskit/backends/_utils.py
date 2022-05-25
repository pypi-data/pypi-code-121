import re


def get_account_slug(sw_backend_name: str):
    _, account_slug = get_provider_and_account(sw_backend_name)
    return account_slug


def get_provider_and_account(sw_backend_name: str):
    m = re.search("^([\w\-]+)\.([\w\-]+)\.", sw_backend_name)
    if not m:
        return None

    return m.groups()


def get_provider_details(sw_backend_name: str):
    # e.g. provider-slug.account-slug.hub.group.project.backend-name
    Ibm_with_details_backend_name_schema = (
        "^([\w\-]+)\.([\w\-]+)\.([\w\-]+)\.([\w\-]+)\.([\w\-]+)\.([\w\-\.]+)$"
    )

    m = re.fullmatch(Ibm_with_details_backend_name_schema, sw_backend_name)
    info = {}

    if m:
        provider, account_slug, hub, group, project, backend = m.groups()
        info["provider"] = provider
        info["account_slug"] = account_slug
        info["details"] = {
            "hub": hub,
            "group": group,
            "project": project,
        }
        info["backend_name"] = backend
        return info

    # e.g. provider-slug.account-slug.backend-name
    backend_name_base_scheme = "^([\w\-]+)\.([\w\-]+)\.([\w\-.]+)$"
    m = re.fullmatch(backend_name_base_scheme, sw_backend_name)
    if m:
        provider, account_slug, backend = m.groups()
        info["provider"] = provider
        info["account_slug"] = account_slug
        info["backend_name"] = backend
        return info
    return {}
