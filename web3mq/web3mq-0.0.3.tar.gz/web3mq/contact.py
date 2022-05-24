"""web3mq contact apis"""

def add_user_to_my_contact(reqhandler, user_id: str) -> str:
    """Add an user to your contact list by user's OID

    :return data:
        if success return none else return errmsg
    """
    payload = {
        'user_id': user_id
    }
    result = reqhandler.post_request('/contacts', payload, return_raw_result=True)
    return result['msg']


def get_my_contact(reqhandler, page: int, size: int):
    """Get contact's info

    see RESTful api docs:
        https://docs.web3messaging.online/docs/Web3MQ-RESTFul-API/Contact/get-contacts#get-contacts-info-1
    """
    result = reqhandler.get_request('/contacts/{}/{}'.format(page, size), {})
    return result
