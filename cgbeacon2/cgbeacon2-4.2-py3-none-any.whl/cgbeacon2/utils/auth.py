# -*- coding: utf-8 -*-
import logging
from typing import Union

import jwt  # https://github.com/jpadilla/pyjwt
import requests
from authlib.jose import jwt as jjwt
from authlib.jose.errors import (
    ExpiredTokenError,
    InvalidClaimError,
    InvalidTokenError,
    MissingClaimError,
)
from cgbeacon2.constants import (
    EXPIRED_TOKEN_SIGNATURE,
    INVALID_TOKEN_AUTH,
    INVALID_TOKEN_CLAIMS,
    MISSING_PUBLIC_KEY,
    MISSING_TOKEN,
    MISSING_TOKEN_CLAIMS,
    NO_GA4GH_USERDATA,
    PASSPORTS_ERROR,
    WRONG_SCHEME,
)

LOG = logging.getLogger(__name__)
GA4GH_SCOPES = ["openid", "ga4gh_passport_v1"]


def validate_token(request, database) -> bool:
    """Validate an auth token contained in the request header.

    Accepts:
        request(flask.request) request received by server
        database(pymongo.database.Database)

    Returns:
        validated(bool): return True if token is valid
    """
    validated = False
    if "X-Auth-Token" not in request.headers:
        return validated
    token = request.headers.get("X-Auth-Token")
    query = {"token": token}
    authorized_user = database["user"].find_one(query)
    validated = bool(authorized_user)
    if validated:
        LOG.info(
            'Authorized user with id "{0}" submits a {1} request'.format(
                authorized_user["_id"], request.method
            )
        )
    return validated


# Authentication code is based on:
# https://elixir-europe.org/services/compute/aai
def authlevel(request, oauth2_settings) -> tuple:
    """Returns auth level from a request object

    Accepts:
        request(flask.request) request received by server
        oauth2_settings(dict) Elixie AAI Oauth2 settings (server, issuers, userinfo)

    Returns:
        auth_level(tuple): ([],bool) == (controlled_access datasets, bona_fide_status)

    """
    token = None

    auth_level = (
        [],
        False,
    )  # (controlled datasets the user has access to, bona fide status)

    if "Authorization" not in request.headers:
        return ([], False)

    try:
        scheme, token = request.headers.get("Authorization").split(" ")
    except ValueError:
        return MISSING_TOKEN
    if scheme != "Bearer":
        return WRONG_SCHEME
    if token == "":
        return MISSING_TOKEN

    public_key = elixir_key(oauth2_settings["server"])
    if public_key == MISSING_PUBLIC_KEY:
        return MISSING_PUBLIC_KEY

    claims_options = claims(oauth2_settings)

    # try decoding the token and getting query permissions
    try:
        decoded_token = jjwt.decode(token, public_key, claims_options=claims_options)
        decoded_token.validate()  # validate the token contents

        LOG.info("Auth Token validated.")
        LOG.info(f'Identified as {decoded_token["sub"]} user by {decoded_token["iss"]}.')

        # retrieve Elixir AAI passports associated to the user described by the auth token
        all_passports = ga4gh_passports(decoded_token, token, oauth2_settings)

        if all_passports == NO_GA4GH_USERDATA:
            return NO_GA4GH_USERDATA
        if all_passports is None:
            return ([], False)

        # collect bona fide requirements from app config file
        bona_fide_terms = oauth2_settings.get("bona_fide_requirements")
        # controlled_ds, bona_fide_ds = check_passports(g44gh_passports)
        auth_level = check_passports(all_passports, bona_fide_terms)

        if auth_level == PASSPORTS_ERROR:
            return PASSPORTS_ERROR

    except MissingClaimError:
        return MISSING_TOKEN_CLAIMS
    except InvalidClaimError:
        return INVALID_TOKEN_CLAIMS
    except InvalidTokenError:
        return INVALID_TOKEN_AUTH
    except ExpiredTokenError:
        return EXPIRED_TOKEN_SIGNATURE
    except Exception as ex:
        return {"errorCode": 403, "errorMessage": str(ex)}

    return auth_level


def elixir_key(server) -> Union[dict, list]:
    """Retrieves Elixir AAI public key from Elixir JWK server

    Accepts:
        server(str). HTTP address to an Elixir server providing public key

    Returns:
        key(json) json content of the server response or Error
    """
    try:
        r = requests.get(server)
        return r.json()

    except Exception:
        return MISSING_PUBLIC_KEY


def claims(oauth2_settings) -> dict:
    """Set up web tokens claims options

    Accepts:
        oauth2_settings(dict): dictionary of OAuth2 settings

    Returns:
        claims(dict): a dictionary describing json token web claims
    """

    claims = dict(
        iss=dict(essential=True, values=",".join(oauth2_settings.get("issuers", []))),
        aud=dict(
            essential=oauth2_settings.get("verify_aud", False),
            values=",".join(oauth2_settings.get("audience", [])),
        ),
        exp=dict(essential=True),
    )
    return claims


def check_passports(passports, bona_fide_terms) -> Union[dict, tuple]:
    """Check userinfo provided by GA4GH
    GA4GH passports are described by this document: https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md
    # Code based on https://github.com/CSCfi/beacon-python/blob/master/beacon_api/permissions/ga4gh.py

    Accepts:
        passports(list)
        bona_fide_terms(str): link to a document where the terms to be a bona fide researcher are stated

    Returns:
        controlled_datasets(set), bona_fide_datasets(set)
    """

    registered_passports = []
    bona_fide_passports = []

    try:
        for passport in passports:
            # Decode encoded passport
            header, payload = decode_passport(passport)
            # get passport passport type
            access_type = payload.get("ga4gh_visa_v1", {}).get("type")
            # has access to controlled access datasets
            if access_type == "ControlledAccessGrants":
                registered_passports.append((passport, header))
            # possible bona fide passport
            if access_type in ["AcceptedTermsAndPolicies", "ResearcherStatus"]:
                bona_fide_passports.append((passport, header, payload))
    except Exception:
        return PASSPORTS_ERROR

    # validate controlled passports and retrieve datasets user has access to
    registered_datasets = get_ga4gh_registered_datasets(registered_passports)

    # validate bona fide passports and retrieve datasets user has access to
    bona_fide_status = is_bona_fide(bona_fide_passports, bona_fide_terms)

    return (list(registered_datasets), bona_fide_status)


def is_bona_fide(bona_fide_passports, bona_fide_terms) -> bool:
    """Retrieve bona fide status based on provided passports

    Documentation from GA4GH: https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#registered-access

    Accepts:
        bona_fide_passports(list): [ (passport(str), header, payload),.. ]
        bona_fide_terms(str): link to a document where the terms to be a bona fide researcher are stated

    Returns:
        True or False
    """
    LOG.info("Getting passport-specific datasets with bona fide access from GA4GH")

    etics = False
    status = False

    for passport in bona_fide_passports:
        validated_status = validate_passport(passport)
        # check if passport is validated. If it's not, skip it
        if validated_status is None:
            continue

        payload = passport[2]
        pass_value = payload.get("ga4gh_visa_v1", {}).get("value")
        pass_type = payload.get("ga4gh_visa_v1", {}).get("type")

        if pass_type in "AcceptedTermsAndPolicies" and pass_value == bona_fide_terms:
            # User accepted bona fide terms specified by bona_fide_terms
            etics = True

        if pass_type == "ResearcherStatus":
            # User was recognized as a researcher -> bona fide status ok
            status = True

    return etics and status  # must be both True


def get_ga4gh_registered_datasets(registered_passports) -> set:
    """Retrieve registered datasets based on provided passports

    Accepts:
        registered_passports(list): [ (passport(str), header),.. ]

    Returns:
        datasets(set): a set of controlled datasets the user has access to
    """
    LOG.info("Getting passport-specific datasets with registered access from GA4GH")
    datasets = set()
    for registered in registered_passports:
        validated_pass = validate_passport(registered)
        if validated_pass is None:
            continue
        dataset = validated_pass.get("ga4gh_visa_v1", {}).get("value").split("/")[-1]
        datasets.add(dataset)

    return datasets


def validate_passport(passport) -> Union[None, dict]:
    """Validate passport claims

    Accepts:
        passport(tuple) : ( passport(str), header ) or ( passport(str), header, payload )

    """
    LOG.info("Validating passport")
    token = passport[0]
    header = passport[1]

    # Beacon can't verify audience because it does not know where the token originated in the first place
    claims_options = {"aud": {"essential": False}}
    try:
        # obtain public key for this passport
        public_key = elixir_key(header.get("jku"))
        # Try decoding the token using the public key
        decoded_passport = jjwt.decode(token, public_key, claims_options=claims_options)
        # And validating the signature
        decoded_passport.validate()
        return decoded_passport
    except Exception as ex:
        LOG.error(f"Error while decoding/validating passport:{ex}")


def decode_passport(encoded) -> tuple:
    """Decode GA4GH passport info
    Passport is a JWT token consisting of 3 strings separated by dots.
    This function extracts info from first and second string (header, payload).
    Signature (3rd string of token) is not used
    (https://pyjwt.readthedocs.io/en/latest/usage.html)

    Accepts:
        passport(str): example --> 76hqhsfyFTJsguays7.88652tgbsjdiaoHGJ5as.99kkd76hhFFRP4g, but longer!

    Returns:
        header(dict), payload(dict). Token's decoded header and payload
    """
    LOG.debug("Decoding a GA4GH passport")

    header = jwt.get_unverified_header(encoded)
    payload = jwt.decode(encoded, options={"verify_signature": False})

    return header, payload


def ga4gh_passports(decoded_token, token, oauth2_settings) -> Union[list, dict]:
    """Check dataset permissions and bona fide status from ga4gh token payload info

    Auth system is described by this document: https://github.com/ga4gh/data-security/blob/master/AAI/AAIConnectProfile.md

    Accepts:
        decoded_token(dict): A JWT token's payload
        token(str): Token provided by request to this beacon
        oauth2_settings(dict): Elixir Oauth2 settings

    Returns:
        passports(list)
    """
    passports = None

    if "scope" not in decoded_token:
        return passports

    token_scopes = decoded_token["scope"].split(" ")

    # If token scopes does NOT overlap with GA4GH scopes, return
    if not all(scope in token_scopes for scope in GA4GH_SCOPES):
        return passports

    # Send a GET request to Elixir userifo endpoint, with token
    passports = ga4gh_userdata(token, oauth2_settings.get("userinfo"))

    if passports == NO_GA4GH_USERDATA:
        return NO_GA4GH_USERDATA

    return passports


def ga4gh_userdata(token, elixir_oidc) -> Union[list, dict]:
    """Sends a request to the Elixir OIDC Broker to retrieve user info (permissions)

    Accepts:
        token(str): token provided by initial request
        elixir_oidc(str): url to Elixir OIDC broker

    Returns:
        passport_info(list)

    """
    LOG.info("Sending a request to Elixir AAI to get userinfo associated to token")
    headers = {"Authorization": f"Bearer {token}"}
    passport_info = None
    try:
        resp = requests.get(elixir_oidc, headers=headers)
        data = resp.json()
        passport_info = data.get("ga4gh_passport_v1")
    except Exception:
        return NO_GA4GH_USERDATA

    return passport_info
