from string import Template
from savitrigen.tree import TreeClass
from savitrigen.config import FrontendConfig
from savitrigen.template.frontend import (
    IndexTemplate,
    ModuleIndexTemplate,
    RouterTemplate,
    StoreTemplate,
    PluginImportTemplate,
    PluginInstanceTemplate,
    InternalRouterTemplate,
    InternalHomeComponentTemplate
)

@TreeClass('frontend')
class FrontendTree():
    def __init__(self, config:FrontendConfig):
        super().__init__()
        self._config = config

    def create(self):
        self.create_build_json()
        self.create_module('internal')

        self.write_file('index.ts', IndexTemplate, {
            'module_imports': self._multiline_replace(
                self._config.plugins,
                PluginImportTemplate,
                lambda _ : {
                    'capitalized': self._capitalize(_.split('-')[-1]),
                    'plugin_name': _
                }
            ),
            'module_instances': self._multiline_replace(
                self._config.plugins,
                PluginInstanceTemplate,
                lambda _ : {
                    'capitalized': ' '*4 + self._capitalize(_.split('-')[-1])
                }
            ),
            'menu_entries': self._multiline_replace(
                self._config.entities.keys(),
                Template(' '*8 + "'dashboard-${entity_name}',"),
                lambda _ : {
                    'entity_name': _
                }
            )
        })

        with self.change_dir('modules/internal'):
            self.write_file('router.ts', InternalRouterTemplate, {})
            self.make_dir('components/dashboard/c-home')
            self.write_file('components/dashboard/c-home/c-home.vue', InternalHomeComponentTemplate, {})

    def create_build_json(self):
        content = self._json_dumps({
            'name': '',
            'externals': {
                'variables': {
                    'productName': self._config.meta.product.name,
                    'productLogo': 'logo.png',
                    'productLogoAlt': 'logo-alt.png',
                    'releases': self._config.has_releases,
                    'notification': self._config.has_notification,
                    'feedback': self._config.has_feedback,

                }
            }
        })

        self.write_file('build.json', content)

    def create_module(self, name:str):
        path = self.make_dir('modules/{}'.format(name))

        store_path = self.make_dir('modules/{}/store'.format(name))
        components_path = self.make_dir('modules/{}/components'.format(name))

        with self.change_dir(path):
            self.write_file('index.ts', ModuleIndexTemplate, {})
            self.write_file('router.ts', RouterTemplate, {})
            self.write_file('store/index.ts', StoreTemplate, {})
