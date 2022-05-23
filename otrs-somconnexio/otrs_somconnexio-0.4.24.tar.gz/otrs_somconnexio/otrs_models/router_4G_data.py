from otrs_somconnexio.otrs_models.internet_data import InternetData


class Router4GData(InternetData):
    type = '4G'

    def __init__(self, **args):
        super().__init__(**args)
