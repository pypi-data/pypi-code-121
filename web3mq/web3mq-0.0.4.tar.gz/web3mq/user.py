"""web3mq user apis"""


def do_register(client, wallet_address: str, platform: str, user_name: str):
    """Binding User to their ETH wallet address

    :return data:
    {
        "user_id": "user's OID",
        "nick_name": "user's nick_name",
        "twitter_username": "user's twitter_username",
        "twitter_avatar": "user's twitter_avatar",
        "instagram_username": "user's instagram_username",
        "instagram_avatar": "user's instagram_avatar",
        "facebook_username": "user's facebook_username",
        "facebook_avatar": "user's facebook_avatar",
        "discord_username": "user's discord_username",
        "discord_avatar": "user's discord_avatar",
        "opensea_username": "user's opensea_username",
        "opensea_avatar": "user's opensea_avatar",
        "eth_wallet_address": "user's eth_wallet_address",
        "ens_name": "user's ens_name",
        "status": "user's status",
        "created_at": "the timestamp when user created"
    }
    """
    payload = {
        'wallet_address': wallet_address.lower(),
        'platform': platform,
        'user_name': user_name
    }
    return client.reqhandler.post_request('/register', payload)


def do_login(client, login_random_secret: str, signature: str, wallet_address: str):
    """Login with MetaMask sign

    :return data:
    {
        "access_token": "your access token",
        "user_info": {
            "user_id": "user's OID",
            "nick_name": "user's nick_name",
            "twitter_username": "user's twitter_username",
            "twitter_avatar": "user's twitter_avatar",
            "instagram_username": "user's instagram_username",
            "instagram_avatar": "user's instagram_avatar",
            "facebook_username": "user's facebook_username",
            "facebook_avatar": "user's facebook_avatar",
            "discord_username": "user's discord_username",
            "discord_avatar": "user's discord_avatar",
            "opensea_username": "user's opensea_username",
            "opensea_avatar": "user's opensea_avatar",
            "eth_wallet_address": "user's eth_wallet_address",
            "ens_name": "user's ens_name",
            "status": "user's status",
            "created_at": "the timestamp when user created"
        }
    }
    """
    payload = {
        'login_random_secret': login_random_secret,
        'signature': signature,
        'wallet_address': wallet_address.lower()
    }
    return client.reqhandler.post_request('/login', payload)


def get_login_random_secret(client, wallet_address: str):
    """Get User's Random Login Secret

    :return data:
        login_random_secret string
    """
    payload = {
        'wallet_address': wallet_address.lower()
    }
    return client.reqhandler.post_request('/login_random_secret', payload)


def get_user_info(client, platform: str, user_name: str):
    """Get user info by platform and username

    :return data:
    {
        "user_id": "user's OID",
        "nick_name": "user's nick_name",
        "twitter_username": "user's twitter_username",
        "twitter_avatar": "user's twitter_avatar",
        "instagram_username": "user's instagram_username",
        "instagram_avatar": "user's instagram_avatar",
        "facebook_username": "user's facebook_username",
        "facebook_avatar": "user's facebook_avatar",
        "discord_username": "user's discord_username",
        "discord_avatar": "user's discord_avatar",
        "opensea_username": "user's opensea_username",
        "opensea_avatar": "user's opensea_avatar",
        "eth_wallet_address": "user's eth_wallet_address",
        "ens_name": "user's ens_name",
        "status": "user's status",
        "created_at": "the timestamp when user created"
    }
    """
    payload = {
        'platform': platform,
        'user_name': user_name
    }
    return client.reqhandler.post_request('/info', payload)


def search_users(client, keyword: str):
    """
        You can use this API to search all users in Swapchat,
        then get user's OID which you want add to your contacts list.

    :return data:
        [{
            "user_id": "user's OID",
            "nick_name": "user's nick_name",
            "twitter_username": "user's twitter_username",
            "twitter_avatar": "user's twitter_avatar",
            "instagram_username": "user's instagram_username",
            "instagram_avatar": "user's instagram_avatar",
            "facebook_username": "user's facebook_username",
            "facebook_avatar": "user's facebook_avatar",
            "discord_username": "user's discord_username",
            "discord_avatar": "user's discord_avatar",
            "opensea_username": "user's opensea_username",
            "opensea_avatar": "user's opensea_avatar",
            "eth_wallet_address": "user's eth_wallet_address",
            "ens_name": "user's ens_name",
            "status": "user's status",
            "created_at": "the timestamp when user created"
        }]
    """

    payload = {
        'keyword': keyword
    }
    return client.reqhandler.post_request('/search', payload, headers=client.get_auth_headers())
