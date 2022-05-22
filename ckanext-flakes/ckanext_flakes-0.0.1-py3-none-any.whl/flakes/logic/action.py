from __future__ import annotations
from typing import Any

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.plugins import get_plugin

from ckanext.toolbelt.decorators import Collector

from ..model import Flake
from . import schema

action, get_actions = Collector("flakes").split()


@action
@validate(schema.flake_create)
def flake_create(context, data_dict):
    """Create flake that can be used as base template for dataset.

    Args:
        name (str, optional): name of the flake
        data (dict): template itself
        parent_id (str, optional): ID of flake to extend
    """

    tk.check_access("flakes_flake_create", context, data_dict)

    sess = context["session"]
    model = context["model"]

    user = model.User.get(context["user"])
    if not user:
        raise tk.NotAuthorized()

    if "parent_id" in data_dict:
        parent = sess.query(Flake).filter_by(id=data_dict["parent_id"]).one_or_none()

        if not parent:
            raise tk.ObjectNotFound()

        if parent.author_id != user.id:
            raise tk.ValidationError({"parent_id": ["Must be owned by the same user"]})

    if "name" in data_dict and Flake.by_name(data_dict["name"], user.id):
        raise tk.ValidationError({"name": ["Must be unique"]})

    flake = Flake(author_id=user.id, **data_dict)
    sess.add(flake)
    sess.commit()

    return flake.dictize(context)


@action
@validate(schema.flake_show)
def flake_show(context, data_dict):
    """Display existing flake

    Args:
        id (str): ID of flake to display
        expand (bool, optional): Extend flake using data from the parent flakes
    """

    tk.check_access("flakes_flake_show", context, data_dict)

    sess = context["session"]
    flake: Flake = sess.query(Flake).filter_by(id=data_dict["id"]).one_or_none()
    if not flake:
        raise tk.ObjectNotFound()

    context["expand"] = data_dict["expand"]

    return flake.dictize(context)


@action
@validate(schema.flake_list)
def flake_list(context, data_dict):
    """Display all flakes of the user.

    Args:
        expand (bool, optional): Extend flake using data from the parent flakes
    """

    tk.check_access("flakes_flake_list", context, data_dict)

    user = context["model"].User.get(context["user"])
    context["expand"] = data_dict["expand"]

    return [flake.dictize(context) for flake in user.flakes]


@action
@validate(schema.flake_update)
def flake_update(context, data_dict):
    """Update existing flake

    Args:
        id (str): ID of flake to update
        data (dict): template itself
        parent_id (str, optional): ID of flake to extend
    """

    tk.check_access("flakes_flake_update", context, data_dict)

    sess = context["session"]
    flake = sess.query(Flake).filter_by(id=data_dict["id"]).one_or_none()

    if not flake:
        raise tk.ObjectNotFound()

    for k, v in data_dict.items():
        setattr(flake, k, v)
    sess.commit()

    return flake.dictize(context)


@action
@validate(schema.flake_delete)
def flake_delete(context, data_dict):
    """Delete existing flake

    Args:
        id (str): ID of flake to update
    """

    tk.check_access("flakes_flake_delete", context, data_dict)

    sess = context["session"]
    flake = sess.query(Flake).filter_by(id=data_dict["id"]).one_or_none()

    if not flake:
        raise tk.ObjectNotFound()

    sess.delete(flake)
    sess.commit()

    return flake.dictize(context)


@action
@validate(schema.flake_lookup)
def flake_lookup(context, data_dict):
    """Search flake by name.

    Args:
        name (str): Name of the flake
    """

    tk.check_access("flakes_flake_lookup", context, data_dict)
    user = context["model"].User.get(context["user"])
    flake = Flake.by_name(data_dict["name"], user.id)

    if not flake:
        raise tk.ObjectNotFound()

    return flake.dictize(context)


@action
@validate(schema.flake_validate)
def flake_validate(context, data_dict):
    """Validate existing flake

    Args:
        id (str): ID of flake to validate
        expand (bool, optional): Extend flake using data from the parent flakes
        schema(str): validation schema for the flake's data
    """

    tk.check_access("flakes_flake_validate", context, data_dict)
    flake = tk.get_action("flakes_flake_show")(context, data_dict)

    return tk.get_action("flakes_data_validate")(
        context,
        {
            "data": flake["data"],
            "expand": data_dict["expand"],
            "schema": data_dict["schema"],
        },
    )


@action
@validate(schema.data_validate)
def data_validate(context, data_dict):
    """Validate arbitrary data against the schema.

    Args:
        data (dict): data that needs to be validated
        schema(str): validation schema for the data
    """

    tk.check_access("flakes_data_validate", context, data_dict)

    schema = _get_schema(data_dict["schema"])
    data, errors = tk.navl_validate(data_dict["data"], schema, context)

    return {
        "data": data,
        "errors": errors,
    }


def _get_schema(name: str) -> dict[str, Any]:
    plugin = get_plugin("flakes")
    schema = plugin.resolve_flake_schema(name)
    return schema
