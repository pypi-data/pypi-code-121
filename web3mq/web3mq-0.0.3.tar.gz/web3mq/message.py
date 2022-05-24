"""web3mq message apis"""

def get_history_messages(
    client,
    room_id: str,
    page: int,
    size: int,
    after_time_stamp: int
):
    """Get History Messages by room oid"""
    payload = {
        'room_id': room_id,
        'page': page,
        'size': size,
        'after_time_stamp': after_time_stamp
    }
    return client.reqhandler.post_request(
        '/messages', payload,
        headers=client.get_auth_headers()
    )
