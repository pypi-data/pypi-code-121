from savitrigen.tree import TreeClass
from savitrigen.config import BackendConfig
from savitrigen.util import map_fields, make_ts_typehints, extract_entities
from savitrigen.template.backend import (
    ControllerTemplate,
    ModelTemplate,
    DocumentImportTemplate,
    ReferenceImportTemplate,
    IndexTemplate,
    PluginImportTemplate,
    PluginInstanceTemplate
)

@TreeClass('backend')
class BackendTree():
    def __init__(self, config:BackendConfig):
        super().__init__()

        self._config = config
        self._unused_keys = [
            'translation',
            'documentation'
        ]

    def create(self):
        self.copy_file('sample.env', '.env')
        self.write_file('index.ts', IndexTemplate, {
            'module_imports': self._multiline_replace(
                self._config.plugins,
                PluginImportTemplate,
                lambda _ : {
                    'capitalized': self._capitalize(_.split('-')[-1]),
                    'plugin_entity': _
                },
            ),
            'module_instances': self._multiline_replace(
                self._config.plugins,
                PluginInstanceTemplate,
                lambda _ : {
                    'capitalized': ' '*4 + self._capitalize(_.split('-')[-1])
                }
            )
        })

        for k, v in self._config.entities.items():
            self.create_entity(k, v)

    def create_build_json(self):
        content = self.json_dumps({})
        self.write_file('build.json', content)

    def create_entity(self, name:str, _description:dict):
        """Creates entities

        Each module is supposed to contain 3 files:
            - index.json
            - moduleName.controller.ts
            - moduleName.model.ts

        Will also add a description to the controller file that may contain JSDoc symbols.
        """
        path = self.make_dir('entities/{}'.format(name))

        description = dict(module=name) | _description.__dict__
        description['fields'] = description.pop('_fields')

        documentation = description.get('documentation').strip()

        fields = _description.fields
        mapped_fields = map_fields(fields)

        entities = list(extract_entities(fields))
        entities_names = [ entity[0] for entity in entities ]

        for k in self._unused_keys:
            if k in description:
                del description[k]

        params = {
            'pascal_case': self._pascal_case(name),
            'camel_case': self._camel_case(name),
            'documentation': documentation,
            'type_hints': make_ts_typehints(mapped_fields),
            **({
                'document_imports': self._multiline_replace(
                    entities_names,
                    DocumentImportTemplate,
                    lambda _ : {
                        'pascal_case': self._pascal_case(_),
                        'camel_case': self._camel_case(_)
                    }
                ),
                'reference_imports': self._multiline_replace(
                    entities_names,
                    ReferenceImportTemplate,
                    lambda _ : {
                        'camel_case': self._camel_case(_),
                    }
                ),

            } if len(entities) > 0 else {})
        }

        with self.change_dir(path):
            self.write_file('index.json', self._json_dumps(description))
            self.write_file('{}.controller.ts'.format(name), ControllerTemplate, params)

            self.write_file('{}.model.ts'.format(name), ModelTemplate, {
                'document_imports': '// no document imports',
                'reference_imports': '// no reference imports',
            }, params)


