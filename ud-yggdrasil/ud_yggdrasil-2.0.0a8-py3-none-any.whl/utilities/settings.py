import yaml

from yggdrasil import drivers


class SettingsException(Exception):
    def __init__(self, error: str):
        self.message = 'Cannot parse settings file:\n{0}'.format(error)
        super().__init__(self.message)


class Settings(object):
    def __init__(self, meta: {}, base_types: [], config_apps:[]):
        self.meta = meta
        self.base_types = base_types
        self.config_apps = config_apps

    @classmethod
    def _check_compatibility(cls, file_yaml):
        classes_apps = drivers.AppGeneric.__subclasses__()
        # Checks that there's a single unique match for all base_types
        for info_driver in file_yaml['base_types']:
            AppsMatching = [App for App in classes_apps if info_driver['type'] == App.identifier]
            if len(AppsMatching) == 0:
                raise SettingsException(
                    "Settings base type '{0}' does not match any internal App class".format(info_driver['type']))
            if len(AppsMatching) > 1:
                raise SettingsException("Several drivers classes match type '{0}'".format(info_driver['type']))
        # Checks that no two drivers configurations have the same name
        all_names = [config['name'] for config in file_yaml['configurations']]
        if len(set(all_names)) != len(all_names):
            raise SettingsException("Several configurations bear the same 'name' attribute")
        # Checks that each configuration relates to a single base type & implements attributes accordingly
        for config in file_yaml['configurations']:
            if 'type' not in config:
                raise SettingsException("No type attributed for configuration {0}".format(config['name']))
            types_matching = [base_type for base_type in file_yaml['base_types'] if base_type['type'] == config['type']]
            if len(types_matching) == 0:
                raise SettingsException(
                    "No base type identified in settings file for configuration of {0}".format(config['name']))
            if len(types_matching) > 1:
                raise SettingsException(
                    "Several base types in settings identified matching type of configuration for '{0}'".format(
                        config['name']))
            type_info = types_matching[0]
            atts_required = type_info['atts_required']
            atts_optional = type_info['atts_optional']

            for att in atts_required:
                if att not in config.keys():
                    raise SettingsException(
                        "Configuration '{0}' does not have required attribute {1}".format(config['name'], att))
            for att in config.keys():
                if att not in atts_required + atts_optional:
                    raise SettingsException(
                        "Attribute '{0}' (configuration {1}) is not accepted for type {2}".format(att, config['name'],
                                                                                                  type_info['type']))

    @classmethod
    def from_yaml(cls, path, safe: bool = True):
        with open(path) as f:
            try:
                settings = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
        if safe:
            cls._check_compatibility(file_yaml=settings)
        return Settings(
            meta=settings['meta'],
            base_types=settings['base_types'],
            config_apps=settings['configurations'],
        )
