# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import http.cookies
import json
import os
from os.path import expanduser
from pathlib import Path
import typing
import nacl.pwhash
import nacl.signing
import numpy as np

DIR_LOGIN_PATH = expanduser("~") + os.sep + ".shapelets"
LOGIN_FILE_PATH = DIR_LOGIN_PATH + os.sep + ".profile.json"

os.environ['PATH'] += os.pathsep + str(Path.home() / '.shapelets/libs')


def read_user_from_login_file(address, user_name=None):
    """
    This function read the user information from the login file.
    :param address: String with the server name.
    :param user_name: String with the username.
    :return: user information.
    """
    return _read_user_from_login_file(DIR_LOGIN_PATH, LOGIN_FILE_PATH, address, user_name)


def register_new_login(server_name, user_name, password, port: int = None, default_user: bool = None):
    """
    This function registers new the user information to a login file.
    :param server_name: String with the server name.
    :param user_name: String with the username.
    :param password: String with the username password.
    :param port: Integer with the port number.
    :param default_user: Boolean: select True to register a default user
    """
    if _add_entry_to_login_file(DIR_LOGIN_PATH, LOGIN_FILE_PATH, server_name, user_name,
                                password, port, default_user):
        print(f"User {user_name} added successfully for address {server_name}")


def remove_user_from_login_file(server_name, user_name):
    """
    This function remove the user information from the login file.
    :param server_name: String with the server name.
    :param user_name: String with the username.
    """
    if _remove_entry_from_login_file(LOGIN_FILE_PATH, server_name, user_name):
        print(f"User {user_name} removed successfully for address {server_name}")


def set_default_user(server_name, user_name):
    """
    This function set an existing user as default.
    :param server_name: String with the server name.
    :param user_name: String with the username.
    """
    if _add_default_user(LOGIN_FILE_PATH, server_name, user_name):
        print(f"User {user_name} set as default successfully for address {server_name}")


def update_user_password(server_name, user_name, old_password, new_password):
    """
    This function update password of an existing user.
    :param server_name: String with the server name.
    :param user_name: String with the username.
    :param old_password: String with the old password.
    :param new_password: String with the new password.
    """
    if _update_user_password(DIR_LOGIN_PATH, LOGIN_FILE_PATH, server_name, user_name,
                             old_password, new_password):
        print(f"Password for user {user_name} updated successfully for address {server_name}")


def _read_user_from_login_file(dir_path, file_path, address, user_name=None):
    _create_login_directory(dir_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            file_data = json.load(file)
            if user_name:
                for user_information in file_data:
                    if (user_information.get("user") == user_name and
                            user_information.get("server") == address):
                        return user_information
            else:
                for user_information in file_data:
                    if (user_information.get("server") == address and
                            user_information.get("default")):
                        return user_information
    return None


def _add_entry_to_login_file(dir_path, file_path, server_name, user_name, password,
                             port: int = None, default: bool = None):
    try:
        new_entry = {
            "server": server_name,
            "user": user_name,
            "password": password,
            "port": port,
            "default": default
        }
        _create_login_directory(dir_path)
        default_user_for_address = None
        if default:
            default_user_for_address = _find_default_user(file_path, server_name)
            if not default_user_for_address and default_user_for_address is not None:
                return False
        if os.path.isfile(file_path):
            with open(file_path, 'r+') as file:
                file_data = json.load(file)
                for user_information in file_data:
                    if (user_information.get("user") == user_name and
                            user_information.get("server") == server_name):
                        print(f"User {user_name} already existed for address {server_name}")
                        return False
                if default_user_for_address:
                    file_data[file_data.index(default_user_for_address)]["default"] = None
                file_data.append(new_entry)
                file.seek(0)
                file.truncate()
                json.dump(file_data, file, indent=4)
                return True
        else:
            with open(file_path, 'w') as file:
                json.dump([new_entry], file, indent=4)
            return True
    except (KeyError, IndexError, ValueError):
        return False


def _remove_entry_from_login_file(file_path, server_name, user_name):
    try:
        with open(file_path, 'r+') as file:
            file_data = [dict(t) for t in {tuple(d.items()) for d in json.load(file)}]
            for user_info in file_data:
                if user_info["server"] == server_name and user_info["user"] == user_name:
                    file_data.remove(user_info)
            file.seek(0)
            file.truncate()
            json.dump(file_data, file, indent=4)
        return True
    except (KeyError, IndexError):
        return False


def _create_login_directory(dir_path):
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


def _add_default_user(file_path, server_name, user_name):
    default_user = _find_default_user(file_path, server_name)
    if not default_user and default_user is not None:
        return False
    if os.path.isfile(file_path):
        with open(file_path, 'r+') as file:
            file_data = json.load(file)
            for user_information in file_data:
                if (user_information.get("user") == user_name and
                        user_information.get("server") == server_name):
                    user_information["default"] = True
            if default_user:
                file_data[file_data.index(default_user)]["default"] = None
            file.seek(0)
            file.truncate()
            json.dump(file_data, file, indent=4)
    return True


def _find_default_user(file_path, server_name):
    if os.path.isfile(file_path):
        with open(file_path, 'r+') as file:
            file_data = json.load(file)
            for user_information in file_data:
                if (user_information.get("server") == server_name and
                        user_information.get("default")):
                    print(f"User {user_information.get('user')} is set as default user for address"
                          f" {user_information.get('server')}")
                    answer = _get_input("Would you like to replace default user? Yes/No")
                    if answer in ["No", "no", "n", "N"]:
                        return False
                    return user_information
    return None


def _get_input(text):
    return input(text)


def _update_user_password(dir_path, file_path, server_name, user_name, old_password, new_password):
    user_information = _read_user_from_login_file(dir_path, file_path, server_name, user_name)
    if user_information and user_information["password"] == old_password:
        _remove_entry_from_login_file(file_path, user_information["server"],
                                      user_information["user"])
        user_information["password"] = new_password
        _add_entry_to_login_file(dir_path, file_path, user_information["server"],
                                 user_information["user"], user_information["password"],
                                 user_information["port"], user_information["default"])
        return True
    return False


def _get_salt_pk(password):
    import libnacl as sodium
    salt = bytes(np.random.randint(0, 256, 16, dtype=np.ubyte))
    seed = nacl.pwhash.argon2id.kdf(size=sodium.crypto_sign_SEEDBYTES,
                                    password=bytes(password, encoding='UTF-8'),
                                    salt=salt,
                                    opslimit=nacl.pwhash.argon2id.OPSLIMIT_MIN,
                                    memlimit=nacl.pwhash.argon2id.MEMLIMIT_MIN)
    (public, _) = sodium.crypto_sign_seed_keypair(seed)
    return salt, public


def _sign_nonce(password, challenge_data):
    """
    This function signs a Nonce.
    :param password: The password of the user.
    :param challenge_data: The challenge to be resolved.
    :return: The signed Nonce.
    """
    import libnacl as sodium
    seed = nacl.pwhash.argon2id.kdf(size=sodium.crypto_sign_SEEDBYTES,
                                    password=bytes(password, encoding='UTF-8'),
                                    salt=bytes(challenge_data['salt']),
                                    opslimit=nacl.pwhash.argon2id.OPSLIMIT_MIN,
                                    memlimit=nacl.pwhash.argon2id.MEMLIMIT_MIN)
    (_, secret) = sodium.crypto_sign_seed_keypair(seed)
    return sodium.crypto_sign_detached(bytes(challenge_data['nonce']), secret)


def _extract_cookies(auth_response) -> typing.Dict:
    """
    This function extracts the cookies from an authentication response.
    :param auth_response: The authentication response.
    :return: The cookies and token of the user session.
    """
    cookies_str = auth_response["headers"].get("set-cookie")
    # Due to Ktor issue: https://github.com/ktorio/ktor/issues/389
    cookies_str = cookies_str.replace("; $x-enc", "")
    cookies_reader = http.cookies.SimpleCookie()
    try:
        cookies_reader.load(cookies_str)
    except http.cookies.CookieError:
        print(f"CookieError parsing: {cookies_str}")
        return None
    auth = cookies_reader.get("shapelets-aut").value
    cnv = cookies_reader.get("shapelets-cnv").value
    return {
        "shapelets-aut": auth,
        "shapelets-cnv": cnv
    }
