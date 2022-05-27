import yaml


class ConfigParser:
    def __init__(self, path: str) -> None:
        self.config_dict = self._read_yml(path)
        self.security = self.config_dict.get('security')
        self.title = self.config_dict.get('title', 'FastAPI')
        self.description = self.config_dict.get('description', '')
        self.version = self.config_dict.get('version', '0.1.0')    
        self.routes = self.config_dict.get('routes', {})   
        self.tags = self._get_tags()

    def _read_yml(self, catalog_path):
        with open(catalog_path, 'r') as stream:
            try:
                return(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                raise exc

    def _get_tags(self):
        tags, metadata = self.config_dict.get('tags'), []
        if tags:
            keys = tags.keys()
            for key in keys:
                metadata.append({'name': key, **tags[key]})
        return metadata