from psu_base.classes.Log import Log

log = Log()

# Example Finti result:
# {
#     "id": 135,
#     "app_code": "BIO_DATA",
#     "app_title": "Biographic Data"
# },


class Application:
    id = None
    code = None
    title = None

    def __init__(self, finti_dict=None):
        if type(finti_dict) is dict:
            self.id = finti_dict["id"]
            self.code = finti_dict["app_code"]
            self.title = finti_dict["app_title"]

    @classmethod
    def global_app(cls):
        instance = cls()
        instance.id = 0
        instance.code = "GLOBAL"
        instance.title = "Global"
        return instance

    @classmethod
    def gather(cls, application_list):
        """
        Given a list of Finti application dicts, return a list of Applications
        """
        applications = []
        try:
            if type(application_list) is list:
                for aa in application_list:
                    if type(aa) is dict:
                        applications.append(Application(aa))
            elif type(application_list) is dict:
                applications.append(Application(application_list))
        except Exception as ee:
            log.error(f"Error gathering applications: {str(ee)}")
        return applications
