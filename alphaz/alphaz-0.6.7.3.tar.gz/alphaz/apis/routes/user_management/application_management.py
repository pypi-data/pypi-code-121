from ....utils.api import route, api, Parameter, ParameterMode
from ....models.database.users_definitions import Application
from ....libs.user_management import application_management_lib

from typing import List

CATEGORY = "user-mgt"

@route(
    "user-mgt/applications",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper),
        Parameter("page_index", ptype=int),
        Parameter("page_size", ptype=int),
        Parameter("order_by", ptype=str, default="name"),
        Parameter("direction", ptype=str, default="asc"),
        Parameter("columns", ptype=List[str]),
    ],
    methods=["GET"],
    category=CATEGORY
)
def get_applications():
    return application_management_lib.get_applications(**api.get_parameters())

@route(
    "user-mgt/applications/names",
    logged=True,
    parameters=[
        Parameter("name", ptype=str, mode=ParameterMode.IN_LIKE, function=str.upper)
    ],
    methods=["GET"],
    category=CATEGORY
)
def get_applications_names():
    return application_management_lib.get_applications_names(**api.get_parameters())

@route(
    "user-mgt/applications/names-id",
    logged=True,
    category=CATEGORY
)
def get_applications_names_and_id():
    return application_management_lib.get_applications_names_and_id(**api.get_parameters())


@route(
    "user-mgt/application",
    logged=True,
    parameters=[
        Parameter("name", required=True),
    ],
    methods=["GET"],category=CATEGORY
)
def get_application():
    return application_management_lib.get_application(**api.get_parameters())


@route(
    "user-mgt/application",
    logged=True,
    parameters=[
        Parameter("application", required=True, ptype=Application),
    ],
    methods=["POST"],category=CATEGORY
)
def create_application():
    return application_management_lib.create_application(**api.get_parameters())


@route(
    "user-mgt/application",
    logged=True,
    parameters=[
        Parameter("application", required=True, ptype=Application),
    ],
    methods=["PUT"],category=CATEGORY
)
def edit_application():
    return application_management_lib.edit_application(**api.get_parameters())


@route(
    "user-mgt/application",
    logged=True,
    parameters=[
        Parameter("id", required=True, ptype=int),
    ],
    methods=["DELETE"],category=CATEGORY
)
def delete_application():
    return application_management_lib.delete_application(**api.get_parameters())

