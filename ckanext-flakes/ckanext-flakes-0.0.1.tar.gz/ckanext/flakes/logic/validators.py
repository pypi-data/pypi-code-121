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
