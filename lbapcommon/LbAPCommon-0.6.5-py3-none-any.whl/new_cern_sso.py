import logging
import requests
import time
import uuid
from requests_gssapi import HTTPSPNEGOAuth, OPTIONAL
from bs4 import BeautifulSoup

from http.cookiejar import MozillaCookieJar, Cookie
from urllib.parse import parse_qs


def save_cookies_lwp(cookiejar, filename):
    """Saves cookies from a requests.Session cookies member into a file in the Netscape format"""

    lwp_cookiejar = MozillaCookieJar()
    for c in cookiejar:
        args = dict(vars(c).items())
        args["rest"] = args["_rest"]
        del args["_rest"]
        if args["expires"] == None:
            args["expires"] = int(time.time()) + 86400
        c = Cookie(**args)
        lwp_cookiejar.set_cookie(c)
    lwp_cookiejar.save(filename, ignore_discard=True)


def post_session_saml(session, response):
    """Performs the SAML POST request given a session and a successful Keycloak authentication response in SAML"""

    soup_saml = BeautifulSoup(response.text, features="html.parser")
    action = soup_saml.form.get("action")
    post_key = soup_saml.form.input.get("name")
    post_value = soup_saml.form.input.get("value")
    session.post(action, data={post_key: post_value})


def login_with_kerberos(login_page, verify_cert, auth_hostname, silent):
    """Simulates a browser session to log in using SPNEGO protocol"""

    session = requests.Session()
    if not silent:
        logging.info("Fetching target URL and its redirects")
    r_login_page = session.get(login_page, verify=verify_cert)
    if "login.cern.ch" in r_login_page.url:
        raise NotImplementedError("Tried to hit old CERN SSO")
    if not silent:
        logging.debug("Landing page: {}".format(r_login_page.url))
        logging.info("Parsing landing page to get the Kerberos login URL")
    soup = BeautifulSoup(r_login_page.text, features="html.parser")
    kerberos_button = soup.find(id="social-kerberos")
    if not kerberos_button:
        error_message = get_error_message(r_login_page.text)
        if error_message:
            raise Exception("Login failed: {}".format(error_message))
        else:
            raise Exception(
                "Login failed: Landing page not recognized as the CERN SSO login page.")
    kerberos_path = kerberos_button.get("href")
    if not silent:
        logging.info("Fetching Kerberos login URL")
    r_kerberos_redirect = session.get(
        "https://{}{}".format(auth_hostname, kerberos_path)
    )
    if not silent:
        logging.info("Logging in using Kerberos Auth")
    r_kerberos_auth = session.get(
        r_kerberos_redirect.url,
        auth=HTTPSPNEGOAuth(mutual_authentication=OPTIONAL),
        allow_redirects=False,
    )
    while (
        r_kerberos_auth.status_code == 302
        and auth_hostname in r_kerberos_auth.headers["Location"]
    ):
        r_kerberos_auth = session.get(
            r_kerberos_auth.headers["Location"], allow_redirects=False
        )
    if r_kerberos_auth.status_code != 302:
        if "login-actions/consent" in r_kerberos_auth.text:
            raise Exception(
                "Login failed: This application requires consent. Please accept it manually before using this tool.")
        error_message = get_error_message(r_kerberos_auth.text)
        if not error_message:
            logging.debug(
                "Not automatically redirected: trying SAML authentication")
            post_session_saml(session, r_kerberos_auth)
        else:
            raise Exception("Login failed: {}".format(error_message))
    return session, r_kerberos_auth


def get_error_message(response_html):
    soup_err_page = BeautifulSoup(response_html, features="html.parser")
    error_message = soup_err_page.find(id="kc-error-message")
    if not error_message:
        return None
    else:
        return error_message.find("p").text


def save_sso_cookie(url, file, verify_cert, auth_hostname, silent=False):
    """Log in into a URL that redirects to the SSO and save the session cookies"""

    try:
        session, response = login_with_kerberos(
            url, verify_cert, auth_hostname, silent=silent)
        if response.status_code == 302:
            redirect_uri = response.headers["Location"]
            if not silent:
                logging.info(
                    "Logged in. Fetching redirect URL to get application cookies")
            session.get(redirect_uri, verify=verify_cert)
        if not silent:
            logging.info("Saving cookies in {}".format(file))
        save_cookies_lwp(session.cookies, file)
    except Exception as e:
        logging.error(
            "An error occurred while trying to log in and save cookies.")
        raise e


def get_sso_token(url, clientid, verify_cert=True, auth_hostname="auth.cern.ch", auth_realm="cern", silent=False):
    """Get an OIDC token by logging in in the Auhtorization URL using Kerberos

    :param url: Application or Redirect URL. Required for the OAuth request.
    :param clientid: Client ID of a client with implicit flow enabled.
    :param verify_cert: Verify certificate.
    :param auth_hostname: Keycloak hostname.
    :param auth_realm: Authentication realm.
    :param silent: Flag for printing log messages (default: False).
    """
    try:
        random_state = str(uuid.uuid4()).split("-")[0]
        authz_url = "https://{}/auth/realms/{}/protocol/openid-connect/auth?client_id={}&response_type=code&state={}&redirect_uri={}".format(
            auth_hostname, auth_realm, clientid, random_state, url
        )
        login_response = login_with_kerberos(
            authz_url, verify_cert, auth_hostname, silent=silent)[1]
        authz_response = parse_qs(
            login_response.headers["Location"].split("?")[1])

        if authz_response["state"][0] != random_state:
            raise Exception(
                "The authorization response doesn't contain the expected state value.")

        r = requests.post(
            "https://{}/auth/realms/{}/protocol/openid-connect/token".format(
                auth_hostname, auth_realm
            ),
            data={
                "client_id": clientid,
                "grant_type": "authorization_code",
                "code": authz_response["code"][0],
                "redirect_uri": url,
            },
        )

        if not silent:
            if not r.ok:
                logging.error(
                    "The token response was not successful: {}".format(r.json()))
                r.raise_for_status()

        token_response = r.json()

        return token_response["access_token"]
    except Exception as e:
        if not silent:
            logging.error(
                "An error occurred while trying to fetch user token."
            )
        raise e
