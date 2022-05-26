from extras.plugins import PluginConfig


class NetBoxAppSystemConfig(PluginConfig):
    name = 'netbox_app_systems'
    verbose_name = 'Application Systems'
    description = 'Netbox plugin. Assign devices and virtual machines to application systems'
    version = '0.1'
    author = 'Oleg Senchenko'
    author_email = 'senchenkoob@mail.ru'
    base_url = 'app-systems'


config = NetBoxAppSystemConfig
