from ....utils.api import route, api, Parameter, ParameterMode
from ....libs.user_management import permission_management_lib
from ....models.database.users_definitions import Permission

from typing import List

CATEGORY = "user-mgt"

@route(
    "user-mgt/permissions",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper),
        Parameter("page_index", ptype=int),
        Parameter("page_size", ptype=int),
        Parameter("order_by", ptype=str, default="key"),
        Parameter("direction", ptype=str, default="asc"),
        Parameter("columns", ptype=List[str]),
    ],
    methods=["GET"],category=CATEGORY
)
def get_permissions():
    return permission_management_lib.get_permissions(**api.get_parameters())

@route(
    "user-mgt/permissions/names",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper),
    ],
    methods=["GET"],category=CATEGORY
)
def get_permissions_names():
    return permission_management_lib.get_permissions_names(**api.get_parameters())

@route(
    "user-mgt/permission",
    logged=True,
    parameters=[
        Parameter("name", required=True, ptype=str),
    ],
    methods=["GET"],category=CATEGORY
)
def get_permission():
    return permission_management_lib.get_permission(**api.get_parameters())


@route(
    "user-mgt/permission",
    logged=True,
    parameters=[
        Parameter("permission", required=True, ptype=Permission),
    ],
    methods=["POST"],category=CATEGORY
)
def create_permission():
    return permission_management_lib.create_permission(**api.get_parameters())


@route(
    "user-mgt/permission",
    logged=True,
    parameters=[
        Parameter("permission", required=True, ptype=Permission),
    ],
    methods=["PUT"],category=CATEGORY
)
def edit_permission():
    return permission_management_lib.edit_permission(**api.get_parameters())


@route(
    "user-mgt/permission",
    logged=True,
    parameters=[
        Parameter("key", required=True, ptype=str),
    ],
    methods=["DELETE"],category=CATEGORY
)
def delete_permission():
    return permission_management_lib.delete_permission(**api.get_parameters())
