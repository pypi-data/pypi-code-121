from alphaz.models.database.users_definitions import Application
from core import core
from typing import List


DB = core.db
LOG = core.get_logger("api")


def get_applications(
    name: str,
    page_index: int,
    page_size: int,
    order_by: str,
    direction: str,
    columns: List[str] = None,
):
    return DB.select(
        Application,
        filters=[Application.name.like(name)],
        disabled_relationships=[Application.roles],
        page=page_index,
        per_page=page_size,
        order_by=order_by,
        order_by_direction=direction,
        columns=columns,
    )

def get_applications_names(name:str):
    return DB.select(
        Application,
        optional_filters={Application.name:{'like':name}},
        unique=Application.name,
        distinct=Application.name,
        order_by=Application.name.asc()
    )

def get_applications_names_and_id():
    return DB.select(Application, columns=[Application.name, Application.id])


def get_application(name: str):
    return DB.select(Application, filters=[Application.name == name], first=True)


def create_application(application: Application):
    return DB.add(application)


def edit_application(application: Application):
    return DB.update(application)


def delete_application(id: int):
    return DB.delete(Application, filters=[Application.id == id])
