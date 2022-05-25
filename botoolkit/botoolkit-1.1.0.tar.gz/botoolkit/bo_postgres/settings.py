from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bopostgres'

TEMPLATES_DIR_PATH = Path(__file__).parent.absolute() / 'templates'

TEMPLATE_CONF_FILE_PATH = (
    TEMPLATES_DIR_PATH / f'{TOOL_NAME}.conf'
)

BASE_DB_IMAGE_SCHEMA_TEMPLATE_PATH = TEMPLATES_DIR_PATH / 'base_db_image_schema.yaml'

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_postgres.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_postgres.commands:ConfigureBOPostgresCommand',
        'run = botoolkit.bo_postgres.commands:RunPostgresServiceCommand',
        'run webbb = botoolkit.bo_postgres.commands:RunWebBBPostgresServiceCommand',
        'create base images = botoolkit.bo_postgres.commands:CreateBaseDBImageCommand',
        'generate base db image schema = botoolkit.bo_postgres.commands:GenerateBaseDBImageSchemaCommand',
        'check access = botoolkit.bo_postgres.commands:CheckDBAccessCommand',
    ],
}
