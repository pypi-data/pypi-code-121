from __future__ import annotations

from typing import Any, Callable

from ckan.plugins import Interface


class IFlakes(Interface):
    """Extend functionality of ckanext-flakes"""

    def get_flake_schemas(self) -> dict[str, dict[str, Any]]:
        """Register named validation schemas.

        Used by `flakes_flake_validate` and `flakes_data_validate` actions.

        Returns:
            Mapping of names and corresponding validation schemas.

        Example:
            def get_flake_schemas(self) -> dict[str, dict[str, Any]]:
                return {
                    "name-only": {"name": [not_missing]}
                }
        """
        return {}

    def get_flake_factories(
        self,
    ) -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
        """Register named example factories.

        Used by `flakes_data_example` action.

        Returns:
            Mapping of names and corresponding example factories.

        Example:
            def get_flake_factories(self) -> dict[str, dict[str, Any]]:
                def factory(payload: dict[str, Any]):
                    return {"field": "value"}

                return {
                    "test-factory": factory
                }
        """
        return {}
