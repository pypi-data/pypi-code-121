from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.classes.Log import Log

log = Log()

# Example Finti result:
# {
#     "permission_id": 169,
#     "status": "A",
#     "app_name": "GLOBAL",
#     "authority_id": 1,
#     "authority_code": "developer",
#     "authority_title": "Developer",
#     "authority_description": "Full access in non-prod. Extra debug info in all environments.",
#     "username": "mjg",
#     "via": "Direct Assignment",
#     "auth_method": "U",
#     "date_assigned": "2020-09-03 16:45:40"
#     "date_revoked": null,
# },


class Permission:
    id = None
    app_code = None
    authority_id = None
    authority_code = None
    authority_title = None
    authority_description = None
    username = None
    via = None
    date_assigned = None
    date_revoked = None

    def __init__(self, finti_dict=None):
        if type(finti_dict) is dict:
            self.id = finti_dict["permission_id"]
            self.app_code = finti_dict["app_name"]
            self.authority_id = finti_dict["authority_id"]
            self.authority_code = finti_dict["authority_code"]
            self.authority_title = finti_dict["authority_title"]
            self.authority_description = finti_dict["authority_description"]
            self.username = finti_dict["username"]
            self.via = finti_dict["via"]
            self.date_assigned = ConvenientDate(finti_dict["date_assigned"])
            self.date_revoked = ConvenientDate(finti_dict["date_revoked"])

            if self.via != "Direct Assignment" and not self.username:
                self.username = "Multiple Users"

    @classmethod
    def gather(cls, permission_list):
        """
        Given a list of Finti permission dicts, return a list of Permissions
        """
        permissions = []
        try:
            if type(permission_list) is list:
                for pp in permission_list:
                    if type(pp) is dict:
                        permissions.append(Permission(pp))
            elif type(permission_list) is dict:
                permissions.append(Permission(permission_list))
        except Exception as ee:
            log.error(f"Error gathering permissions: {str(ee)}")
        return permissions
