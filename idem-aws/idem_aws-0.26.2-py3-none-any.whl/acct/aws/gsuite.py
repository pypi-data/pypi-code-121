import datetime
import io
import os
import re
import sys
import tempfile
from typing import Any
from typing import Dict
from typing import Tuple

import msgpack
from cryptography.fernet import Fernet
from dict_tools import data

try:
    import aws_google_auth

    HAS_GOOGLE_AUTH = True
except ImportError as e:
    HAS_GOOGLE_AUTH = False, str(e)


def __virtual__(hub):
    return HAS_GOOGLE_AUTH


def __init__(hub):
    # Initialize a directory where credentials can be stored
    hub.acct.aws.gsuite.TMP = os.path.join(
        tempfile.gettempdir(), "idem", "aws_google_acct"
    )
    os.makedirs(hub.acct.aws.gsuite.TMP, exist_ok=True)


def parse_opts(
    hub,
    role_arn: str,
    username: str = None,
    password: str = None,
    duration: int = None,
    idp_id: str = None,
    region: str = None,
    sp_id: str = None,
    resolve_aliases: bool = None,
    account: str = None,
    keyring: str = None,
    saml_assertion: str = None,
    saml_cache: bool = True,
    **ctx,
):
    args = data.NamespaceDict(
        {
            "auto_duration": False,
            "duration": duration,
            "idp_id": idp_id,
            "region": region,
            "role_arn": role_arn,
            "sp_id": sp_id,
            "resolve_aliases": resolve_aliases,
            "username": username,
            "account": account,
            "keyring": keyring,
            "saml_assertion": saml_assertion,
            "saml_cache": saml_cache,
            "ask_role": False,
            "disable_u2f": False,
            "profile": None,
            "bg_response": True,
            "save_failure_html": False,
            "print_creds": True,
            "quiet": True,
            "log_level": "warn",
        }
    )

    config = aws_google_auth.resolve_config(args)

    print(
        "You may be prompted to verify your identity on a secondary 2FA device before"
        " this can continue"
    )

    out = io.StringIO()
    get_pass = aws_google_auth.util.Util.get_password

    if password is not None:
        aws_google_auth.util.Util.get_password = lambda *z: password
    sys.stdout = out
    aws_google_auth.process_auth(args, config)
    sys.stdout = sys.__stdout__
    if password is not None:
        aws_google_auth.util.Util.get_password = get_pass

    stripped_out = out.getvalue().strip().replace("\n", "")

    match = re.match(
        "(.*)export AWS_ACCESS_KEY_ID='([^']+)' AWS_SECRET_ACCESS_KEY='([^']+)'"
        " AWS_SESSION_TOKEN='([^']+)' AWS_SESSION_EXPIRATION='([^']+)'(.*)",
        stripped_out,
    )
    if match is None:
        raise ConnectionRefusedError("Could not connect to aws")

    if match.group(1):
        hub.log.info(match.group(1))
    ctx["aws_access_key_id"] = match.group(2)
    ctx["aws_secret_access_key"] = match.group(3)
    ctx["aws_session_token"] = match.group(4)
    ctx["region_name"] = config.region
    session_expiration = match.group(5)
    if match.group(6):
        hub.log.info(match.group(6))
    return ctx, session_expiration


async def load_profile(hub, enc_profile: str) -> Tuple[Dict[str, Any], str]:
    if os.path.exists(enc_profile):
        try:
            ret = await hub.crypto.init.decrypt_file(
                acct_key=hub.OPT.acct.acct_key,
                acct_file=enc_profile,
                crypto_plugin="fernet",
            )
            return ret["boto_creds"], ret["expiration"]
        except Exception as e:
            hub.log.error(e)

    return {}, ""


def dump_profile(hub, enc_profile: str, boto_creds: Dict[str, Any], expiration: str):
    hub.log.debug(f"Writing encrypted aws acct information to {enc_profile}")
    f = Fernet(hub.OPT.acct.acct_key)
    with open(enc_profile, "wb+") as wfh:
        data = {"boto_creds": boto_creds, "expiration": expiration}
        wfh.write(f.encrypt(msgpack.dumps(data)))


async def gather(hub, profiles) -> Dict[str, Any]:
    """
    Generate AWS credentials from Google Auth

    Example:
    .. code-block:: yaml

        aws.gsuite:
          profile_name:
            username: example@gmail.com
            password: please_don't_use_this
            role_arn: arn:aws:iam::999999999:role/xacct/developer
            idp_id: XXXXXXXXX
            sp_id: 999999999999
            region: us-east-1
            duration: 36000
            account: developer
    """
    sub_profiles = data.NamespaceDict()
    for profile, ctx in profiles.get("aws.gsuite", {}).items():
        enc_profile = os.path.join(hub.acct.aws.gsuite.TMP, f"{profile}.fernet")
        # Try to load existing account information
        boto_creds, expiration = await hub.acct.aws.gsuite.load_profile(enc_profile)
        try:
            expiration = datetime.datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            expiration = None

        # Recreate the session if it expired or doesn't exist
        if not (
            boto_creds
            or (expiration and expiration < datetime.datetime.now(expiration.tzinfo))
        ):
            boto_creds, expiration = hub.acct.aws.gsuite.parse_opts(**ctx)
            # Save the account information to an encrypted file
            hub.acct.aws.gsuite.dump_profile(enc_profile, boto_creds, expiration)
        else:
            hub.log.debug(
                f"Found existing google-aws-auth credentials in {enc_profile}"
            )

        # Strip any args that were used for authentication
        sub_profiles[profile] = boto_creds

    return sub_profiles
