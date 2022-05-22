import sys
import yaml
import logging
import re
from sdap.utils import get_log

logger = get_log(__name__)


# This loads all collections,
# TODO if we want a serverless application, we should do otherwise
class CollectionLoader:

    PRIMITIVE_TYPES = (int, float, str, list)

    def __init__(self, conf_file, secret_file=None):
        self._conf_file = conf_file
        self._secret_file = secret_file
        self.camel_2_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')

        with open(conf_file, 'r') as stream:
            self.conf = yaml.load(stream, yaml.Loader)

            if secret_file:
                self._add_secrets(self.conf, secret_file)

            self.collections = {}
            for key, desc in self.conf['collections'].items():
                self.collections[key] = self.desc_to_instances(desc)

    def get_collections(self):
        return [c for c in self.conf['collections']]

    @staticmethod
    def _add_secrets(conf, secret_file):
        with open(secret_file, 'r') as secret_stream:
            secrets = yaml.load(secret_stream, yaml.Loader)
            for c_name, c_desc in conf['collections'].items():
                if c_name in secrets:
                    c_desc['args'].update(secrets[c_name])

        return conf

    def get_driver(self, collection):
        return self.collections[collection]

    def get_collection_list(self):
        return list(self.conf.keys())

    @staticmethod
    def get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def desc_to_instances(self, desc):
        if isinstance(desc, CollectionLoader.PRIMITIVE_TYPES):
            return desc
        elif isinstance(desc, dict) and 'class' in desc.keys():
            logger.debug("create class %s", desc['class'])
            kls = CollectionLoader.get_class(desc['class'])
            args = {}
            if 'args' in desc.keys():
                for k_camel, v in desc['args'].items():
                    logger.debug('add argument %s', k_camel)
                    k_snake = self.camel_2_snake_pattern.sub('_', k_camel).lower()
                    args[k_snake] = self.desc_to_instances(v)
            return kls(**args)
        else:
            logger.warning('value %s in %s configuration is not supported', desc, self._conf_file)
            return None





