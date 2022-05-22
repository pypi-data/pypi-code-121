from typing import Dict

import attr


WORKER_INSTANCES_JSONSCHEMA = {
    "type": "object",
    "additionalProperties": {"type": "string"},
    "description": "Dictionary of <worker name>:<worker class path>"
}


@attr.frozen
class WorkerSettingsDeclaration:

    # cron syntax
    settings_schema: Dict[str, any]

    required: bool
