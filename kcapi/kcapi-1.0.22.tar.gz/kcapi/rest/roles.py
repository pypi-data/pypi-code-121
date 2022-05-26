from .targets import Targets


# The Keycloak guys decided to use another resource DELETE /roles-by-id, instead of sticking to DELETE /roles.
def RolesURLBuilder(url):
    targets = Targets.makeWithURL(url)
    targets.targets['delete'].replaceResource('roles', 'roles-by-id')
    targets.targets['update'].replaceResource('roles', 'roles-by-id')
    return targets