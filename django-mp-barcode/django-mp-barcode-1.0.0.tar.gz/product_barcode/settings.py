
class BarCodeSettings(object):

    @property
    def INSTALLED_APPS(self):
        apps = super().INSTALLED_APPS + ['product_barcode']

        if not 'solo' in apps:
            apps.append('solo')

        return apps


default = BarCodeSettings
