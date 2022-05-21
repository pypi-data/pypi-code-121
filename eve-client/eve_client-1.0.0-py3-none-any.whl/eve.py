import json
import logging
from asyncio import exceptions
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from urllib.parse import urljoin

import dateutil.parser
import nacl.encoding
import nacl.exceptions
import nacl.public
import nacl.utils
import requests

from eve_client.helper import notify, verify_email

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
LOG = logging.getLogger("EVE Client")


class EVEClient:
    """Class client to communicate with the Exodus API.

    This module allows to connect and interact with the
    Exodus Intelligence API.

    Example initiate connection:

        >>> from eve_client import eve
        >>> exodus_api = eve.EVEClient( 'email',
                                        'password',
                                        'private_key',
                                        'url')

    Note: See help(EVEClient) for more information.

    """

    def __init__(
        self, email, password, key=None, url="https://vpx.exodusintel.com"
    ) -> None:
        """Init the Client class.

        Args:
            email (str): Email address registered with Exodus Intelligence.
            password (str): User password
            key (str, optional): Exodus Intelligence API key. Defaults to None.
        """
        self.url = url
        if not self.url.lower().startswith(
            "http://"
        ) and not self.url.lower().startswith("https://"):
            self.url = "https://" + self.url

        if verify_email(email):
            self.email = email
        self.session = requests.Session()
        self.password = password
        self.private_key = key
        self.token = self.get_access_token()

    def get_access_token(self):
        """Obtain access token.

        Raises:
            ConnectionError: When a connection to API is unavailable.

        Returns:
            str: The token.
        """
        r = self.session.post(
            urljoin(self.url, "vpx-api/v1/login"),
            json={"email": self.email, "password": self.password},
        )
        if r.status_code != 200:
            notify(r.status_code, "Authentication problem.")
            raise requests.exceptions.ConnectionError("Could not authenticate")
        return r.json()["access_token"]

    def get_bronco_public_key(self):
        """Get server public key.

        Returns:
            str: A string representation of a public key.
        """
        key = None
        try:
            key = self.session.get(
                urljoin(self.url, "vpx-api/v1/bronco-public-key")
            ).json()["data"]["public_key"]
        except (requests.exceptions.ConnectionError, KeyError):
            LOG.warning("Unable to retrieve the Public key.")
        return key

    def decrypt_bronco_in_report(self, report, bronco_public_key):
        """Decrypt the content of a report using a private and public key.

        Args:
            report (object): The encrypted message.
            bronco_public_key (str): The public key

        Returns:
            dict: A dictionary object representing the report.
        """
        ciphertext = b64decode(report["bronco"])
        nonce = ciphertext[0:24]
        ciphertext = ciphertext[24:]
        try:
            unseal_box = nacl.public.Box(
                nacl.public.PrivateKey(b64decode(self.private_key)),
                nacl.public.PublicKey(b64decode(bronco_public_key)),
            )
            plaintext = unseal_box.decrypt(ciphertext, nonce)
        except Exception as e:
            notify(403, f"{e}. Verify your private key.")
            raise KeyError()
        report["bronco"] = json.loads(plaintext)
        return report

    def handle_reset_option(self, reset):
        """Reset number of days.

        Args:
            reset (int): Number of days in the past to reset
            reset (date): A date in ISO8601

        Returns:
            datetime:  A date

        """
        if reset is None:
            return None

        # First, try to load reset as an integer indicating the number of days
        # in the past to reset to
        try:
            reset = abs(int(reset))
            return datetime.utcnow() - timedelta(days=reset)
        except ValueError:
            pass

        # Try to load reset as a ISO8601 datetime
        try:
            reset = dateutil.parser.isoparse(reset)
        except ValueError as e:
            LOG.warning(
                f"Did not recognize '{reset}' as ISO8601 datetime - {e}"
            )
            return None
        return reset

    def get_vuln(self, identifier):
        """Get a Vulnerability by identifier or cve.

        ie: x.get_vuln('CVE-2020-9456') or x.get_vuln('XI-00048890') both
        refer to the same vulnerability.

        Args:
            identifier (str): String representation of vulnerability id.

        Returns:
            dict: Returns a report in json format
        """
        try:
            r = self.session.get(
                urljoin(self.url, f"vpx-api/v1/vuln/for/{identifier}")
            )
            if r.json()["ok"]:
                return r.json()
        except (KeyError, requests.exceptions.ConnectionError):
            return notify(
                404, f"Vulnerability {identifier} not found."
            )

    def get_recent_vulns(self, reset=None):
        """Get all vulnerabilities within 60 days of the user's stream marker;\
             limit of 50 vulnerabilities can be returned.

        Args:
            reset (int): Reset the stream maker to a number of days in the\
                past.

        Returns:
            dict: Returns a list of vulnerabilities.
        """
        params = {}

        # Int or ISO datetime
        if reset:
            reset = self.handle_reset_option(reset)

        # If handle_reset_option returned None
        if reset:
            params = {"reset": reset.isoformat()}

        r = self.session.get(
            urljoin(self.url, "vpx-api/v1/vulns/recent"),
            params=params,
        )

        if r.status_code != 200:
            return notify(
                r.status_code,
                "There was an error retrieving the recent vulnerability list.",
            )
        return r.json()

    def get_recent_reports(self, reset=None):
        """Get list of recent reports.

        Args:
            reset (int): A number of days in the past to reset.
            reset (date): A date in ISO format

        Returns:
            dict: Returns a list of reports.
        """
        params = {}
        if reset:
            reset = self.handle_reset_option(reset)

        if reset:
            reset = reset.isoformat()
            params = {"reset": reset}
        r = self.session.get(
            urljoin(self.url, "vpx-api/v1/reports/recent"),
            params=params,
        )
        if r.status_code != 200:
            return notify(
                r.status_code,
                "Unable to retrieve the recent report list",
            )

        r = r.json()

        if self.private_key and r["ok"]:
            bronco_public_key = self.get_bronco_public_key()
            try:
                r["data"]["items"] = [
                    self.decrypt_bronco_in_report(report, bronco_public_key)
                    for report in r["data"]["items"]
                ]
            except KeyError:
                notify(421, "Unable to decrypt report")
            return r

        return r

    def get_report(self, identifier):
        """Get a report by identifier.

        Args:
            identifier (str): String representation of report id.

        Returns:
            dict: Returns either a report in json format
        """
        r = self.session.get(
            urljoin(self.url, f"vpx-api/v1/report/{identifier}")
        )
        if r.status_code != 200:
            return notify(
                r.status_code,
                f"Couldn't find a report for {identifier}",
            )
        r = r.json()
        if self.private_key:
            # try:
            bronco_public_key = self.get_bronco_public_key()
            self.decrypt_bronco_in_report(r["data"], bronco_public_key)
            # except:
            #     # let decrypt_bronco_in_report handle the issues
            #     pass
        return r

    def get_vulns_by_day(self):
        """Get vulnerabilities by day.

        Returns:
            dict: Returns vulnerabilities list.
        """
        r = self.session.get(urljoin(self.url, "vpx-api/v1/aggr/vulns/by/day"))

        if r.status_code != 200:
            return notify(
                r.status_code,
                "Unable to retrieve vulnerabilities by day.",
            )
        return r.json()

    def generate_key_pair(self):
        """Generate a Key Pair.

        Raises:
            InvalidStateError: Could not set the public key.
            InvalidStateError: Could not confirm the public key.

        Returns:
            tuple: A key pair (sk, pk)
        """
        # Get the CSRF token from the session cookies

        csrf_token = [
            c.value
            for c in self.session.cookies
            if c.name == "csrf_access_token"
        ][0]

        # Generate a public/private key pair
        secret_key = nacl.public.PrivateKey.generate()
        public_key = secret_key.public_key
        # Propose the public key
        r = self.session.post(
            urljoin(self.url, "vpx-api/v1/pubkey"),
            headers={"X-CSRF-TOKEN": csrf_token},
            json={
                "key": public_key.encode(nacl.encoding.Base64Encoder).decode(
                    "utf-8"
                )
            },
        )

        if r.status_code != 200:
            raise exceptions.InvalidStateError(
                f"Couldn't set public key, status code {r.status_code}"
            )

        challenge = b64decode(r.json()["data"]["challenge"])

        # Send the challenge response
        unseal_box = nacl.public.SealedBox(secret_key)
        challenge_response = unseal_box.decrypt(challenge)
        r = self.session.post(
            urljoin(self.url, "vpx-api/v1/pubkey"),
            headers={"X-CSRF-TOKEN": csrf_token},
            json={
                "challenge_response": b64encode(challenge_response).decode(
                    "utf-8"
                )
            },
        )
        if r.status_code != 200:
            raise exceptions.InvalidStateError(
                f"Couldn't confirm public key, status code {r.status_code}"
            )

        return (
            public_key.encode(nacl.encoding.Base64Encoder).decode("utf-8"),
            secret_key.encode(nacl.encoding.Base64Encoder).decode("utf-8"),
        )
