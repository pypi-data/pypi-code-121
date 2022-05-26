from savitrigen.tree import TreeClass
from savitrigen.config.project import ProjectConfig

@TreeClass('..')
class ProjectTree():
    def __init__(self, config:ProjectConfig):
        super().__init__()
        self._config = config

    def create(self):
        self.create_package_json()

    def create_package_json(self):
        dependencies = [
            '@savitri/common',
            '@savitri/backend',
            '@savitri/frontend',
            '@savitri/components'
        ]

        dependencies += self._config.plugins or []
        content = self._json_dumps({
            'dependencies': {
                dep: '*'
                for dep in dependencies
            }
        })

        self.write_file('package.json', content)
