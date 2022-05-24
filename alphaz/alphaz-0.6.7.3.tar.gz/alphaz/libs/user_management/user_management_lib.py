from datetime import datetime
import json

from sqlalchemy import or_, and_, outerjoin
from alphaz.models.database.users_definitions import (
    User,
    UserRole,
    Role,
    RolePermission,
    Application,
)
from alphaz.apis import users
from alphaz.models.main import AlphaException
from core import core

DB = core.db
API = core.api
LOG = core.get_logger("api")
LDAP_DATA = API.conf.get("auth/ldap/user_data")


def get_users(
    name: str,
    application: str,
    role: str,
    permission: str,
    order_by: str,
    direction: str,
    page_index: int = 0,
    page_size: int = 200,
):
    query = (
        DB.session.query(User)
        .distinct(User.username)
        .outerjoin(UserRole, (UserRole.user_id == User.id))
        .outerjoin(Role, (UserRole.role_name == Role.name))
        .outerjoin(RolePermission, (RolePermission.role_name == Role.name))
        .outerjoin(Application, (Role.id_app == Application.id))
    )

    filters = []
    if name is not None:
        filters.append(
            or_(User.mail.ilike(name), User.username.ilike(name))
        )
    
    optional_filters = [
        {
            Application.name: {"ilike": application},
            Role.name: {"ilike": role},
            RolePermission.permission_key: {"ilike": permission},
        }
    ]

    users = DB.select_query(
        query,
        model=User,
        page=page_index,
        per_page=page_size,
        order_by=order_by,
        order_by_direction=direction,
        optional_filters=optional_filters,
        filters=filters
    )
    return users


def get_user(name: str):
    return DB.select(User, filters=[User.username == name], first=True)


def add_user(uid: str):
    if DB.select(User, filters=[User.username == uid]) != []:
        raise AlphaException("user_already_exists")
    res = users.get_ldap_users(f"(uid={uid})")
    if res == []:
        raise AlphaException("user_not_found")
    res = res[0]

    added_infos = users.infos_dict_from_ldap(LDAP_DATA, res)

    user = {
        "username": res["uid"],
        "mail": res["mail"] if "mail" in res else None,
        "date_registred": datetime.now(),
        "infos": json.dumps(added_infos),
    }
    return DB.add(User(**user))
