from psu_base.classes.Log import Log

log = Log()

# Example Finti result:
# {
#     "id": 1,
#     "authority_code": "developer"
#     "authority_title": "Developer",
#     "authority_description": "Full access in non-prod. Extra debug info in all environments.",
# },


class Authority:
    id = None
    code = None
    title = None
    description = None

    def __init__(self, finti_dict=None):
        if type(finti_dict) is dict:
            self.id = finti_dict["id"]
            self.code = finti_dict["authority_code"]
            self.title = finti_dict["authority_title"]
            self.description = finti_dict["authority_description"]

    @classmethod
    def gather(cls, authority_list):
        """
        Given a list of Finti authority dicts, return a list of Authority
        """
        authorities = []
        try:
            if type(authority_list) is list:
                for aa in authority_list:
                    if type(aa) is dict:
                        authorities.append(Authority(aa))
            elif type(authority_list) is dict:
                authorities.append(Authority(authority_list))
        except Exception as ee:
            log.error(f"Error gathering authorities: {str(ee)}")
        return authorities
