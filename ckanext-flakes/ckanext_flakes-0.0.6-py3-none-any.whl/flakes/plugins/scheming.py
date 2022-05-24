from __future__ import annotations

from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ..interfaces import IFlakes


class FlakesSchemingPlugin(p.SingletonPlugin):
    p.implements(IFlakes, inherit=True)

    # IFlakes

    def get_flake_schemas(self):
        return {
            **_get_schemas("fields", "organization", "organization"),
            **_get_schemas("fields", "group", "group"),
            **_get_schemas("dataset_fields", "dataset", "dataset"),
            **_get_schemas("resource_fields", "dataset", "resource"),
        }


def _get_schemas(fields: str, entity: str, category: str) -> dict[str, Any]:
    """Convert entity schemas from scheming into validation schemas."""
    from ckanext.scheming.plugins import _field_create_validators

    try:
        types = tk.get_action(f"scheming_{entity}_schema_list")(
            {"ignore_auth": True}, {}
        )
    except KeyError:
        # Corresponding scheming plugin is not enabled
        return {}

    schemas = {}
    for type_ in types:
        schema = tk.get_action(f"scheming_{entity}_schema_show")(
            {"ignore_auth": True}, {"type": type_}
        )

        schemas[f"scheming_{category}_{type_}"] = {
            f["field_name"]: _field_create_validators(f, schema, False)
            for f in schema[fields]
        }

    return schemas
