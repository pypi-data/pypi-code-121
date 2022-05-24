"""web3mq room apis"""

def create_chat_room(client, user_ids: list):
    payload = {
        'user_id': user_ids
    }
    return client.reqhandler.post_request('/rooms', payload, headers=client.get_auth_headers())


def get_room_info(client, room_id: str):
    """Get Room info by room OID

    see RESTful api docs
        https://docs.web3messaging.online/docs/Web3MQ-RESTFul-API/Room/get-room-info
    """
    return client.reqhandler.get_request('/rooms/' + room_id, {}, headers=client.get_auth_headers())


def get_my_chats(client, page: int, size: int):
    """Get the chat rooms you are participating in

    see RESTful api docs
        https://docs.web3messaging.online/docs/SwapChat/Room/get-chat-rooms#get-the-chat-rooms-you-are-participating-in
    """
    payload = {
        'page': page,
        'size': size
    }
    return client.reqhandler.post_request('/my_chats', payload, headers=client.get_auth_headers())


def get_my_room_ids(client):
    """Get all rooms' id that you are participating in

    see RESTful api docs
        https://docs.web3messaging.online/docs/SwapChat/Room/get-chat-rooms#get-all-rooms-id-that-you-are-participating-in

    :return data:
        [
            "room id",
            "room id"
        ]
    """
    return client.reqhandler.get_request('/my_rooms', {}, headers=client.get_auth_headers())
