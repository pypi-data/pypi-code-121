from extras.plugins import PluginConfig


class NetBoxRisksConfig(PluginConfig):
    name = 'risks'
    verbose_name = 'Risks'
    description = 'Add IS risks related fields to devices and virtual machines'
    version = '0.1'
    base_url = 'risks'
    author = 'Oleg Senchenko'
    author_email = 'senchenkoob@mail.ru'


config = NetBoxRisksConfig
