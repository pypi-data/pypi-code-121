from string import Template

ModelTemplate = Template(
r"""import { mongoose, options, descriptionToSchema } from '@savitri/backend'
import { default as Description } from './index.json'

${document_imports}
${reference_imports}

export interface ${pascal_case}Document extends mongoose.Document {
${type_hints}
}

export const ${pascal_case}Schema = descriptionToSchema<${pascal_case}Document>(Description, options)
export const ${pascal_case} = mongoose.model<${pascal_case}Document>('${pascal_case}', ${pascal_case}Schema)
""")

