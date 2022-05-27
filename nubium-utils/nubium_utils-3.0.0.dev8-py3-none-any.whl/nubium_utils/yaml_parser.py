import yaml
import os


class EnvironmentTag(yaml.YAMLObject):
    yaml_tag = u'!Environment'

    @classmethod
    def from_yaml(cls, loader, node):
        return os.environ[node.value]


yaml.SafeLoader.add_constructor(EnvironmentTag.yaml_tag, EnvironmentTag.from_yaml)


def load_yaml_fp(fp):
    if fp.endswith('.yaml') or fp.endswith('.yml'):
        with open(fp, 'r') as f:
            data = yaml.safe_load(f)
            if 'data' in data:
                data = yaml.safe_load(data['data']['nubium-topics.yaml'])
    else:
        data = yaml.safe_load(fp)
    return data
