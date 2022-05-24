from enrichsdk.app.utils import EnrichAppConfig

class APPNAMEConfig(EnrichAppConfig):
    name = 'APPNAME'
    verbose_name = "APPDESC"
    description = f"APPDESC"
    status = "stable"
    enable = True
    filename = __file__
    multiple = False
    composition = True
