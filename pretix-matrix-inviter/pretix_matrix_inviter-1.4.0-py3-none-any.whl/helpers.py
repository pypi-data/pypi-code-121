import requests
from urllib.parse import quote as url_quote


def matrix_room_info_for_event(event):
    return event.cache.get_or_set(
        "matrix_room_info",
        matrix_room_info(
            event.settings.matrix_inviter_matrix_server,
            event.settings.matrix_inviter_authorization_token,
            event.settings.matrix_inviter_matrix_room,
        ),
        120,
    )


def matrix_room_info(server, token, room_id_or_alias):
    room_id = matrix_room_id(server, room_id_or_alias)
    canonical_alias = matrix_room_canonical_alias_from_id(server, token, room_id)
    name = matrix_room_name_from_id(server, token, room_id)

    return {
        "room_id": room_id,
        "canonical_alias": canonical_alias,
        "name": name,
    }


def matrix_room_id(server, room_id_or_alias):
    if not server or not room_id_or_alias:
        return ""
    elif room_id_or_alias.startswith("!"):
        return room_id_or_alias
    else:
        return matrix_room_id_from_alias(server, room_id_or_alias)


def matrix_room_id_from_alias(server, alias):
    if not server or not alias:
        return ""

    r = requests.get(
        "https://{}/_matrix/client/v3/directory/room/{}".format(
            url_quote(server),
            url_quote(alias),
        ),
    )

    return r.json().get("room_id")


def matrix_room_canonical_alias_from_id(server, token, room_id):
    if not server or not token or not room_id:
        return ""

    r = requests.get(
        "https://{}/_matrix/client/v3/rooms/{}/state/m.room.canonical_alias".format(
            url_quote(server),
            url_quote(room_id),
        ),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
    )

    return r.json().get("alias")


def matrix_room_name_from_id(server, token, room_id):
    if not server or not token or not room_id:
        return ""

    r = requests.get(
        "https://{}/_matrix/client/v3/rooms/{}/state/m.room.name".format(
            url_quote(server),
            url_quote(room_id),
        ),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
    )

    return r.json().get("name")
