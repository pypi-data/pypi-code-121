import vgs_api_client


def config(username, password, host="https://api.sandbox.verygoodvault.com"):
    return vgs_api_client.Configuration(host=host, username=username, password=password)
