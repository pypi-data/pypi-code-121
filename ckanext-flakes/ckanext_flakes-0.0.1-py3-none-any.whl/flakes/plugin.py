from __future__ import annotations

from typing import Any, Optional
import ckan.plugins as p

from .logic import action, auth, validators
from .interfaces import IFlakes


class FlakesPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IValidators)

    _flake_schemas: Optional[dict[str, Any]] = None

    def get_actions(self):
        return action.get_actions()

    def get_auth_functions(self):
        return auth.get_auth()

    def get_validators(self):
        return validators.get_validators()

    def configure(self, config):
        self._flake_schemas = None

    def resolve_flake_schema(self, name: str) -> Optional[Any]:
        if self._flake_schemas is None:
            schemas = {}
            for plugin in p.PluginImplementations(IFlakes):
                schemas.update(plugin.get_flake_schemas())
            self._flake_schemas = schemas

        return self._flake_schemas[name]
