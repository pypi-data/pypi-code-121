from otrs_somconnexio.otrs_models.internet_data import InternetData


class ADSLData(InternetData):
    service_type = 'adsl'

    def __init__(self, **args):
        self.landline_phone_number = args.get("landline_phone_number", "")
        args.pop("landline_phone_number", None)
        super().__init__(**args)
