from __future__ import annotations

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

from ..model import Flake

validator, get_validators = Collector("flakes").split()


@validator
def flake_id_exists(value, context):
    """Flake with the specified ID exists."""
    session = context["session"]

    result = session.query(Flake).filter_by(id=value).one_or_none()
    if not result:
        raise tk.Invalid("Not Found: Flake")
    return value


@validator
def into_api_action(value):
    """Get API action by name."""
    try:
        return tk.get_action(value)
    except KeyError as e:
        raise tk.Invalid(str(e))
