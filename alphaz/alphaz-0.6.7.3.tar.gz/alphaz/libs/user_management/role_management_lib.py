from typing import List

from sqlalchemy import distinct, or_
from sqlalchemy.sql.expression import text
from alphaz.models.database.users_definitions import (
    Role,
    RolePermission,
    UserRole,
    Application,
)
from core import core
from alphaz.models.main import AlphaException


DB = core.db
LOG = core.get_logger("api")


def get_roles(
    name: str,
    application: str,
    permission: str,
    page_index: int,
    page_size: int,
    order_by: str,
    direction: str,
    columns: List[str] = None,
):
    query = (
        DB.session.query(Role)
        .distinct(Role.name)
        .outerjoin(Application, (Role.id_app == Application.id))
        .outerjoin(RolePermission, (Role.name == RolePermission.role_name))
    )
    if permission:
        query = query.filter(or_(RolePermission.permission_key != permission, RolePermission.permission_key == None))
    optional_filters = {
            Application.name: {"like": application},
            Role.name: {"like": name},
        }
    return DB.select_query(
        query,
        model=Role,
        page=page_index,
        per_page=page_size,
        order_by=text(f"role.{order_by}"),
        order_by_direction=direction,
        optional_filters=optional_filters,
    )

def get_roles_names(name:str):
    return DB.select(
        Role,
        distinct=Role.name,
        unique=Role.name,
        optional_filters=[{Role.name:{'ilike':name}}],
        order_by=Role.name.asc()
    )


def get_role(name: str):
    return DB.select(Role, filters=[Role.name == name], first=True)


def create_role(role: Role):
    return DB.add(role)


def edit_role(role: Role):
    return DB.update(role)


def delete_role(name: str):
    return DB.delete(Role, filters=[Role.name == name])


def delete_role_permission(perm_key: str, role_name: str):
    return DB.delete(
        RolePermission,
        filters=[
            RolePermission.permission_key == perm_key,
            RolePermission.role_name == role_name,
        ],
    )


def add_role_permission(perm_key: str, role_name: str):
    return DB.add(
        RolePermission(
            **{"permission_key": perm_key, "role_name": role_name, "activated": True}
        )
    )


def delete_user_role(user_id: int, role_name: str):
    return DB.delete(
        UserRole,
        filters=[
            UserRole.user_id == user_id,
            UserRole.role_name == role_name,
        ],
    )


def add_user_role(user_id: int, role_name: str):
    return DB.add(
        UserRole(**{"user_id": user_id, "role_name": role_name, "activated": True})
    )


def add_app_role(app_id: int, role_name: str):
    role: Role = DB.select(Role, filters=[Role.name == role_name], first=True)
    if not role:
        raise AlphaException("no_role_found")
    role.id_app = app_id
    return DB.update(role)


def delete_app_role(role_name: str):
    role: Role = DB.select(Role, filters=[Role.name == role_name], first=True)
    if not role:
        raise AlphaException("no_role_found")
    role.id_app = None
    return DB.update(role)
