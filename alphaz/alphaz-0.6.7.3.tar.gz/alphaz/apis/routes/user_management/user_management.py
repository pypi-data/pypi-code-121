from ....utils.api import route, api, Parameter, ParameterMode
from ....libs.user_management import user_management_lib
from ....models.database.users_definitions import User

CATEGORY = "user-mgt"

@route(
    "user-mgt/users",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE),
        Parameter("application", ptype=str, mode=ParameterMode.IN_LIKE),
        Parameter("role", ptype=str, mode=ParameterMode.IN_LIKE),
        Parameter("permission", ptype=str, mode=ParameterMode.IN_LIKE),
        Parameter("order_by", ptype=str, default="username"),
        Parameter("direction", ptype=str, default="asc"),
        Parameter("page_index", ptype=int),
        Parameter("page_size", ptype=int),
    ],
    methods=["GET"],category=CATEGORY
)
def get_users():
    return user_management_lib.get_users(**api.get_parameters())


@route(
    "user-mgt/user",
    logged=True,
    parameters=[
        Parameter("name", required=True),
    ],
    methods=["GET"],category=CATEGORY
)
def get_user():
    return user_management_lib.get_user(**api.get_parameters())


@route(
    "user-mgt/user",
    logged=True,
    parameters=[
        Parameter("uid", required=True, ptype=str),
    ],
    methods=["POST"],category=CATEGORY
)
def add_user():
    return user_management_lib.add_user(**api.get_parameters())
