from django.conf import settings
from psu_base.classes.Log import Log

log = Log()

__version__ = "1.1.0"

__all__ = []

# # Default settings
# _DEFAULTS = {
#     "AUTHORIZE_GLOBAL": False,  # Allow authorizing for other apps?
#     # Admin Menu Items
#     "PSU_AUTHORIZE_ADMIN_LINKS": [
#         {
#             "url": "authorize:authorize_index",
#             "label": "Manage Permissions",
#             "icon": "fa-lock",
#             "authorities": "~SecurityOfficer",
#         },
#     ],
# }
#
# # Management of Apps and Authorities is not needed for application-specific use
# try:
#     if getattr(settings, "APP_CODE") in ["SSO", "DEMO"]:
#         _DEFAULTS["PSU_AUTHORIZE_ADMIN_LINKS"].append(
#             {
#                 "url": "authorize:manage_authorities",
#                 "label": "Manage Authorities",
#                 "icon": "fa-id-badge",
#                 "authorities": "~SecurityOfficer",
#             },
#         )
#         _DEFAULTS["PSU_AUTHORIZE_ADMIN_LINKS"].append(
#             {
#                 "url": "authorize:manage_applications",
#                 "label": "Manage Applications",
#                 "icon": "fas fa-th",
#                 "authorities": "~SecurityOfficer",
#             },
#         )
# except:
#     pass
#
# # Assign default setting values
# log.debug("Setting default settings for PSU_AUTHORIZE")
# for key, value in list(_DEFAULTS.items()):
#     try:
#         getattr(settings, key)
#     except AttributeError:
#         setattr(settings, key, value)
#     # Suppress errors from DJANGO_SETTINGS_MODULE not being set
#     except ImportError as ee:
#         log.debug(f"Error importing {key}: {ee}")
