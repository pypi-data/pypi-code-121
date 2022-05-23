import itertools
from sqlalchemy.orm import relationship
from . import sql_lib, secure_lib, json_lib

from ..models.database import main_definitions as defs
from ..models.database.users_definitions import User, UserSession

from core import core

DB = core.db


def __get_user_data_by_identifier_and_password(
    identifier, password_attempt, identifier_type="username", no_password_check:bool=False
):
    user_data = __get_user_data(identifier, identifier_type.lower())

    if user_data is not None and len(user_data) != 0 and password_attempt is not None:
        if no_password_check:
            return user_data
        valid_password = secure_lib.compare_passwords(
            password_attempt, user_data["password"]
        )
        if valid_password:
            return user_data
    return None


def get_user_data_by_username_and_password(username, password_attempt):
    """Get user data from database by username.

    Args:
        mail ([type]): [description]
        password_attempt ([type]): [description]

    Returns:
        [type]: [description]
    """
    return __get_user_data_by_identifier_and_password(
        identifier=username,
        password_attempt=password_attempt,
        identifier_type="username",
    )


def get_user_data_by_mail_and_password(mail, password_attempt):
    """Get user data from database by mail.

    Args:
        mail ([type]): [description]
        password_attempt ([type]): [description]

    Returns:
        [type]: [description]
    """
    return __get_user_data_by_identifier_and_password(
        identifier=mail, password_attempt=password_attempt, identifier_type="mail"
    )


def get_user_data_from_login(login, password=None, no_password_check:bool=False):
    """Get user data from database either by mail or username.

    Args:
        login ([type]): [description]
        password ([type]): [description]

    Returns:
        [type]: [description]
    """
    user_mail = __get_user_data_by_identifier_and_password(
        login, password, identifier_type="mail", no_password_check=no_password_check
    )
    user_username = __get_user_data_by_identifier_and_password(
        login, password, identifier_type="username", no_password_check=no_password_check
    )
    if user_mail is not None:
        return user_mail
    if user_username is not None:
        return user_username
    return None


def __get_user_data(value, column):
    """Get the user associated with given column."""
    user_data = DB.select(
        User,
        filters=[User.__dict__[column] == value],
        first=True,
        json=True,
        relationship=True,
        disabled_relationships=["notifications"],
    )
    if user_data is None:
        return None
    if "user_roles" in user_data:
        user_roles = [
            [
                x["permission_key"]
                for x in y["role"]["role_permissions"]
                if x["activated"] and x["permission"]["activated"]
            ]
            for y in user_data["user_roles"]
            if y["activated"]
        ]
        user_roles = list(itertools.chain(*user_roles))
        user_data["user_roles"] = user_roles
    if "infos" in user_data and type(user_data["infos"]) == dict:
        infos = json_lib.load_json(user_data["infos"])
        infos = {
            x.decode("utf-8")  if hasattr(x,'decode') else x:
            y.decode("utf-8")  if hasattr(y,'decode') else y 
            for x,y in infos.items()
        }
        user_data["infos"] = infos
    return user_data


def get_user_data_by_id(user_id):
    return __get_user_data(user_id, "id")


def get_user_data_by_logged_token(token):
    return __get_user_data(token, "token")


def get_user_data_by_registration_token(token):
    return __get_user_data(token, "registration_token")


def get_user_data_by_password_reset_token(token):
    return __get_user_data(token, "password_reset_token")


def get_user_data_by_mail(mail):
    return __get_user_data(mail, "mail")


def get_user_data_by_username(username):
    return __get_user_data(username, "username")


def get_user_data_by_telegram_id(telegram_id):
    return __get_user_data(telegram_id, "telegram_id")


def update_users():
    """Update all users."""

    # Set expired states if needed
    query = "UPDATE user SET role = 0 WHERE expire <= UTC_TIMESTAMP();"
    DB.execute_query(query, None)

    # Set expired states if needed
    query = "UPDATE user SET password_reset_token = 'consumed' WHERE password_reset_token_expire <= UTC_TIMESTAMP();"
    DB.execute_query(query, None)

    # Remove non activated in time accounts
    query = "DELETE FROM user WHERE role = -1 AND date_registred + INTERVAL 15 MINUTE > UTC_TIMESTAMP();"
    DB.execute_query(query, None)

    # Remove expired sessions
    query = "DELETE FROM user_session WHERE expire <= UTC_TIMESTAMP();"
    DB.execute_query(query, None)


def is_valid_mail(email):  # TODO: update
    return (
        DB.select(
            defs.MailingList,
            filters=[defs.MailingList.email == email],
            distinct=defs.MailingList.email,
            unique=defs.MailingList.email,
            first=True,
        )
        != None
    )


def get_all_address_mails():
    return DB.select(
        defs.MailingList, distinct=defs.MailingList.email, unique=defs.MailingList.email
    )
