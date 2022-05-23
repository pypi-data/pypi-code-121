from typing import List
from ....utils.api import route, api, Parameter, ParameterMode
from ....models.database.users_definitions import Role
from ....libs.user_management import role_management_lib

CATEGORY = "user-mgt"

@route(
    "user-mgt/roles",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper),
        Parameter("application", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper),
        Parameter("permission", ptype=str, function=str.upper),
        Parameter("page_index", ptype=int),
        Parameter("page_size", ptype=int),
        Parameter("order_by", ptype=str, default="name"),
        Parameter("direction", ptype=str, default="asc"),
        Parameter("columns", ptype=List[str]),
    ],category=CATEGORY
)
def get_roles():
    return role_management_lib.get_roles(**api.get_parameters())

@route(
    "user-mgt/roles/names",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper)
    ],category=CATEGORY
)
def get_roles_names():
    return role_management_lib.get_roles_names(**api.get_parameters())

@route(
    "user-mgt/role",
    logged=True,
    parameters=[
        Parameter("name", required=True),
    ],category=CATEGORY
)
def get_role():
    return role_management_lib.get_role(**api.get_parameters())


@route(
    "user-mgt/role",
    logged=True,
    parameters=[
        Parameter("role", required=True, ptype=Role),
    ],
    methods=["POST"],category=CATEGORY
)
def create_role():
    return role_management_lib.create_role(**api.get_parameters())


@route(
    "user-mgt/role",
    logged=True,
    parameters=[
        Parameter("role", required=True, ptype=Role),
    ],
    methods=["PUT"],category=CATEGORY
)
def edit_role():
    return role_management_lib.edit_role(**api.get_parameters())


@route(
    "user-mgt/role",
    logged=True,
    parameters=[
        Parameter("name", required=True, ptype=str),
    ],
    methods=["DELETE"],category=CATEGORY
)
def delete_role():
    return role_management_lib.delete_role(**api.get_parameters())


@route(
    "user-mgt/role/permission",
    logged=True,
    parameters=[
        Parameter("perm_key", required=True, ptype=str),
        Parameter("role_name", required=True, ptype=str),
    ],
    methods=["DELETE"],category=CATEGORY
)
def delete_role_permission():
    return role_management_lib.delete_role_permission(**api.get_parameters())

@route(
    "user-mgt/role/permission",
    logged=True,
    parameters=[
        Parameter("perm_key", required=True, ptype=str),
        Parameter("role_name", required=True, ptype=str),
    ],
    methods=["POST"],category=CATEGORY
)
def add_role_permission():
    return role_management_lib.add_role_permission(**api.get_parameters())


@route(
    "user-mgt/role/user",
    logged=True,
    parameters=[
        Parameter("user_id", required=True, ptype=int),
        Parameter("role_name", required=True, ptype=str),
    ],
    methods=["DELETE"],category=CATEGORY
)
def delete_user_role():
    return role_management_lib.delete_user_role(**api.get_parameters())

@route(
    "user-mgt/role/user",
    logged=True,
    parameters=[
        Parameter("user_id", required=True, ptype=int),
        Parameter("role_name", required=True, ptype=str),
    ],
    methods=["POST"],category=CATEGORY
)
def add_user_role():
    return role_management_lib.add_user_role(**api.get_parameters())

@route(
    "user-mgt/role/application",
    logged=True,
    parameters=[
        Parameter("app_id", required=True, ptype=int),
        Parameter("role_name", required=True, ptype=str),
    ],
    methods=["POST"],category=CATEGORY
)
def add_app_role():
    return role_management_lib.add_app_role(**api.get_parameters())

@route(
    "user-mgt/role/application",
    logged=True,
    parameters=[
        Parameter("role_name", required=True, ptype=str),
    ],
    methods=["DELETE"],category=CATEGORY
)
def delete_app_role():
    return role_management_lib.delete_app_role(**api.get_parameters())
