from string import Template

"""Used in models"""
DocumentImportTemplate = Template(
r"import { ${pascal_case}Document } from '../${camel_case}/${camel_case}.model'"
)

ReferenceImportTemplate = Template(
r"import '../${camel_case}/${camel_case}.model'"
)


"""Used in index"""
PluginImportTemplate = Template(
r"import { backend as ${capitalized}Module } from '$plugin_entity'"
)

PluginInstanceTemplate = Template(
r"${capitalized}Module(),"
)
