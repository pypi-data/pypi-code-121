from ikologikapi.domain.AbstractIkologikObject import AbstractIkologikObject


class Domain(AbstractIkologikObject):

    def __init__(self):
        super().__init__()

        self.name = None
        self.allowHttp = True
        self.allowHttps = True
        self.host = None
        self.port = 443

        self.titleText = None
        self.footerText = None
        self.poweredByActive = True

        self.loginInfoActive = True
        self.loginInfoOpenByDefault = True
        self.loginInfoUrl = '/assets/theme/info.html'
