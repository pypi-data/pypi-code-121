from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan.authz import is_authorized

from ckanext.toolbelt.decorators import Collector

from ..model import Flake

auth, get_auth = Collector("flakes").split()

CONFIG_CREATION_ALLOWED = "ckanext.flakes.creation.allowed"
CONFIG_VALIDATION_ALLOWED = "ckanext.flakes.validation.allowed"

DEFAULT_CREATION_ALLOWED = True
DEFAULT_VALIDATION_ALLOWED = False


@auth
def flake_create(context, data_dict):
    if not tk.asbool(
        tk.config.get(CONFIG_CREATION_ALLOWED, DEFAULT_CREATION_ALLOWED)
    ):
        return {"success": False}

    author = context["model"].User.get(context["user"])

    if "parent_id" in data_dict:
        parent = (
            context["session"]
            .query(Flake)
            .filter_by(id=data_dict["parent_id"])
            .one_or_none()
        )
        if not parent or parent.author_id != author.id:
            return {"success": False}

    return {"success": True}


def _valdiation_allowed():
    return tk.asbool(
        tk.config.get(CONFIG_VALIDATION_ALLOWED, DEFAULT_VALIDATION_ALLOWED)
    )


def _owns_flake(context: dict[str, Any], id_: str) -> bool:
    flake = context["session"].query(Flake).filter_by(id=id_).one_or_none()
    return bool(flake and flake.author.name == context["user"])


@auth
def flake_show(context, data_dict):
    return {"success": _owns_flake(context, data_dict["id"])}


@auth
def flake_update(context, data_dict):
    return {"success": _owns_flake(context, data_dict["id"])}


@auth
def flake_override(context, data_dict):
    return is_authorized("flakes_flake_create", context, data_dict)


@auth
def flake_lookup(context, data_dict):
    return {"success": True}


@auth
def flake_list(context, data_dict):
    return {"success": True}


@auth
def flake_delete(context, data_dict):
    return {"success": _owns_flake(context, data_dict["id"])}


@auth
def flake_validate(context, data_dict):
    return {
        "success": _valdiation_allowed()
        and _owns_flake(context, data_dict["id"])
    }


@auth
def data_validate(context, data_dict):
    return {"success": _valdiation_allowed()}


@auth
def data_example(context, data_dict):
    return {"success": _valdiation_allowed()}


@auth
def flake_materialize(context, data_dict):
    return {"success": _owns_flake(context, data_dict["id"])}


@auth
def flake_combine(context, data_dict):
    return {
        "success": all(_owns_flake(context, id_) for id_ in data_dict["id"])
    }


@auth
def flake_merge(context, data_dict):
    ids: list[str] = list(data_dict["id"])
    if "destination" in data_dict:
        ids.append(data_dict["destination"])

    return {"success": all(_owns_flake(context, id_) for id_ in ids)}
