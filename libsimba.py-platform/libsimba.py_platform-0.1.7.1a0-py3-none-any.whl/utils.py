import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlencode, urlunparse
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class SearchFilter(dict):
    def __init__(self, **kwargs):
        self.update(dict(**kwargs))

    @property
    def query_args(self):
        search_terms = self.keys()
        query_args = dict()
        [
            query_args.update(
                {
                    "filter[{}]".format(search_term.replace("__", ".")): self.get(
                        search_term
                    )
                }
            )
            for search_term in search_terms
        ]
        return query_args


def token_expired(token_data: dict, offset: int = 60):
    """
    Checks to see if a token has expired, by checking the 'expires' key
    Adds an offset to allow for delays when performing auth processes

    :param token_data: the data dict to check for expiry. Should contain an 'expires' key
    :param offset: To allow for delays in auth processes, this number of seconds is added to the expiry time
    :return:
    """
    if "expires" in token_data:
        expires = token_data["expires"]
        now_w_offset = datetime.now() + timedelta(seconds=offset)
        expiry = datetime.fromtimestamp(expires)
        if now_w_offset >= expiry:
            log.debug("Saved token expires within 60 seconds")
            return True
        log.debug("Saved token valid for at least 60 seconds")
        return False
    else:
        log.info("No expiry date stored for token, assume expired")
        return True


def save_token(client_id: str, token_data: dict):
    """
    Saves the token data to a file.

    Checks the TOKEN_DIR environment variable for alternative token storage locations,
    otherwise uses the current working path

    Creates the token directory if it doesn't already exist.

    Adds an "expires" key to the auth token data, set to time "now" added to the expires_in time
    This is used later to discover if the token has expired

    Token files are named <client_id>_token.json

    :param client_id: The ID for the client, token files are named <client_id>_token.json
    :param token_data: The tokeauth data to save
    :return:
    """
    token_dir = os.getenv("TOKEN_DIR", "./")
    os.makedirs(token_dir, exist_ok=True)
    token_file = os.path.join(token_dir, "{}_token.json".format(client_id))
    with open(token_file, "w") as t1:
        expiry_date = datetime.now() + timedelta(seconds=int(token_data["expires_in"]))
        token_data["expires"] = int(expiry_date.timestamp())
        json.dump(token_data, t1)
        log.info("Saved token : {}".format(token_file))


def get_saved_token(client_id: str):
    """
    Checks a local directory for a file containing an auth token
    If present, check the token hasn't expired, otherwise return it

    Raises exceptions if the token directory is missing,
    or if there is no token file,
    or if the token has expired, see def token_expired(token_data)

    Checks the TOKEN_DIR environment variable for alternative token storage locations,
    otherwise uses the current working path

    Token files are named <client_id>_token.json

    :param client_id: The ID for the client, token files are named <client_id>_token.json
    :return: a dict of the token data, retrieved from the token file.
    """
    token_dir = os.getenv("TOKEN_DIR", "./")
    if os.path.isdir(token_dir):
        token_file = os.path.join(token_dir, "{}_token.json".format(client_id))
        if os.path.isfile(token_file):
            with open(token_file, "r") as t1:
                token_data = json.load(t1)
                log.debug("Found saved token : {}".format(token_file))

                if token_expired(token_data):
                    raise Exception("Token expiry date elapsed")
                return token_data
        raise Exception("Token file not found")
    raise Exception("Token dir not found")


def build_url(base_api_url, path, args_dict):
    # Returns a list in the structure of urlparse.ParseResult
    url_parts = list(urlparse(base_api_url))
    url_parts[2] = path
    url_parts[4] = urlencode(args_dict)
    return urlunparse(url_parts)
