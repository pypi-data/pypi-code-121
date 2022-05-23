from alphaz.models.database.users_definitions import Permission
from core import core
from typing import List


DB = core.db
LOG = core.get_logger("api")


def get_permissions(
    name: str,
    page_index: int,
    page_size: int,
    order_by: str,
    direction: str,
    columns: List[str] = None,
):
    return DB.select(
        Permission,
        filters=[Permission.key.like(name)],
        disabled_relationships=[Permission.role_permissions],
        page=page_index,
        per_page=page_size,
        order_by_direction=direction,
        order_by=order_by,
        columns=columns,
    )

def get_permissions_names(name:str):
    return DB.select(
        Permission,
        optional_filters={Permission.key:{'like':name}},
        unique=Permission.key,
        distinct=Permission.key,
        order_by=Permission.key.asc()
    )

def get_permission(name: str):
    return DB.select(Permission, filters=[Permission.key == name], first=True)


def create_permission(permission: Permission):
    return DB.add(permission)


def edit_permission(permission: Permission):
    return DB.update(permission)


def delete_permission(key: str):
    return DB.delete(Permission, filters=[Permission.key == key])
