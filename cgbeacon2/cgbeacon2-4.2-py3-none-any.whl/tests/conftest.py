# -*- coding: utf-8 -*-
import time

import mongomock
import pytest
from authlib.jose import jwt
from cgbeacon2.server import create_app

DATABASE_NAME = "testdb"
GA4GH_SCOPES = ["openid", "ga4gh_passport_v1"]


@pytest.fixture(scope="function")
def mock_user(request):
    """Define a mock user to be used when testing REST API services"""
    user = dict(
        id="test_id",
        name="User Name",
        description="I'm a test user",
        url="someurl",
    )
    return user


@pytest.fixture(scope="function")
def pymongo_client(request):
    """Get a client to the mongo database"""
    mock_client = mongomock.MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE_NAME)

    request.addfinalizer(teardown)
    return mock_client


@pytest.fixture(scope="function")
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = pymongo_client
    database = mongo_client[DATABASE_NAME]
    return database


@pytest.fixture
def mock_app(database):
    """Create a test app to be used in the tests"""
    app = create_app()
    app.db = database

    # fix test oauth2 params for the mock app
    return app


@pytest.fixture
def basic_query(test_snv):
    """A basic allele query"""
    params = dict(
        assemblyId=test_snv["assemblyId"],
        referenceName=test_snv["referenceName"],
        start=test_snv["start"],
        referenceBases=test_snv["referenceBases"],
        alternateBases=test_snv["alternateBases"],
    )
    return params


@pytest.fixture
def test_snv():
    """A dictionary representing a snv variant as it is saved in database"""
    variant = {
        "_id": "572dca7bd95dc2f288a0dbcfee2df7d2",
        "referenceName": "1",
        "start": 235878452,
        "startMin": 235878452,
        "startMax": 235878452,
        "end": 235878453,
        "endMin": 235878453,
        "endMax": 235878453,
        "referenceBases": "G",
        "alternateBases": "GTTT",
        "assemblyId": "GRCh37",
        "datasetIds": {"public_ds": {"samples": {"ADM1059A1": {"allele_count": 2}}}},
        "call_count": 2,
    }
    return variant


@pytest.fixture
def test_sv():
    """A dictionary representing a sv variant as it is saved in database"""
    variant = {
        "_id": "8623a1f2d1ba887bafed174ab3eb5d41",
        "referenceName": "5",
        "start": 474601,
        "end": 474974,
        "referenceBases": "GCGGGGAGAGAGAGAGAGCGAGCCAGGTTCAGGTCCAGGGAGGAGAGAGACAGCGCGCGCGAGGCGGAGACCTGGAGGGAGAGGAGCTGCGGAGAGGGGTTAGGCGGGGAGGGAGAGAGCCAGGTTCAGGTCCAGGGAGGAGAGAGACAGCGCGCGCGAGGCGGAGACCTGGAGGGAGAGGAGCTGCGGAGAGGGGTTAGGCGGGGAGAGAGAGAGCGAGCCAGGTTCAGGTCCAGGGAGGAGAGAGACAGCGCGCGCGAGGCGGAGACCTGGAGGGAGAGGAGCTGCGGAGAGGGGTTAGGCGGGGAGGGAGAGAGACAGCGCGCGCGAGGCGGAGACCTGGAGGGAGAGGAGCTGCGGAGAGGGGTTAGGC",
        "alternateBases": "GT",
        "variantType": "DEL",
        "assemblyId": "GRCh37",
        "datasetIds": {"public_ds": {"samples": {"ADM1059A1": {"allele_count": 1}}}},
        "call_count": 1,
    }
    return variant


@pytest.fixture
def test_bnd_sv():
    """A dictionary representing a BND sv variant as it is saved in database"""
    variant = {
        "_id": "c0e355e7899e9fd765797c9f72d0cf7f",
        "referenceName": "17",
        "mateName": "2",
        "start": 198981,
        "end": 321680,
        "referenceBases": "A",
        "alternateBases": "A]2:321681]",
        "variantType": "BND",
        "assemblyId": "GRCh37",
        "datasetIds": {"test_public": {"samples": {"ADM1059A1": {"allele_count": 1}}}},
        "call_count": 1,
    }
    return variant


@pytest.fixture
def public_dataset():
    """A test public dataset dictionary"""
    dataset = dict(
        _id="public_ds",
        name="Public dataset",
        assembly_id="GRCh37",
        authlevel="public",
        description="Public dataset description",
        version="v1.0",
        url="external_url.url",
    )
    return dataset


@pytest.fixture
def registered_dataset():
    """A test dataset dictionary with registered authlevel"""
    dataset = dict(
        _id="registered_ds",
        name="Registered dataset",
        assembly_id="GRCh37",
        authlevel="registered",
        description="Registered dataset description",
        version="v1.0",
        url="external_registered_url.url",
    )
    return dataset


@pytest.fixture
def controlled_dataset():
    """A test dataset dictionary with controlled authlevel"""
    dataset = dict(
        _id="controlled_ds",
        name="Controlled dataset",
        assembly_id="GRCh37",
        authlevel="controlled",
        description="Controlled dataset description",
        version="v1.0",
        url="external_regostered_url.url",
    )
    return dataset


@pytest.fixture
def public_dataset_no_variants():
    """A test dataset dictionary"""
    dataset = dict(
        _id="dataset2",
        name="Test dataset 2",
        assembly_id="GRCh37",
        authlevel="public",
        description="Test dataset 2 description",
        version="v1.0",
        url="external_url2.url",
        consent_code="FOO",
    )
    return dataset


@pytest.fixture
def gene_objects_build37():
    """A list containing 3 test genes as they are saved in gene collection"""
    gene1 = {
        "_id": "5f84572c3804912d9618d867",
        "ensembl_id": "ENSG00000171314",
        "hgnc_id": 8888,
        "symbol": "PGAM1",
        "build": "GRCh37",
        "chromosome": "10",
        "start": 99185917,
        "end": 99193198,
    }
    gene2 = {
        "_id": "5f84572c3804912d9618dd25",
        "ensembl_id": "ENSG00000121236",
        "hgnc_id": 16277,
        "symbol": "TRIM6",
        "build": "GRCh37",
        "chromosome": "11",
        "start": 5617339,
        "end": 5634188,
    }
    gene3 = {
        "_id": "5f84572c3804912d96191f9b",
        "ensembl_id": "ENSG00000016391",
        "hgnc_id": 24288,
        "symbol": "CHDH",
        "build": "GRCh37",
        "chromosome": "3",
        "start": 53846362,
        "end": 53880417,
    }
    return [gene1, gene2, gene3]


@pytest.fixture
def test_gene():
    """A test gene object in the same format as it's saved in the database"""
    gene = {
        "_id": "5f8815f638049161e6ee429c",
        "ensembl_id": "ENSG00000128513",
        "hgnc_id": 17284,
        "symbol": "POT1",
        "build": "GRCh37",
        "chromosome": "7",
        "start": 124462440,
        "end": 124570037,
    }
    return gene


########### Security-related fixtures ###########
# https://github.com/mpdavis/python-jose/blob/master/tests/test_jwt.py


@pytest.fixture
def mock_oauth2(pem):
    """Mock OAuth2 params for the mock app"""

    mock_params = dict(
        server="FOO",
        issuers=["https://login.elixir-czech.org/oidc/"],
        userinfo="mock_oidc_server",  # Where to send access token to view user data (permissions, statuses, ...)
        audience=["audience"],
        verify_aud=True,
    )
    return mock_params


@pytest.fixture
def payload():
    """Token payload"""
    expiry_time = round(time.time()) + 60
    claims = {
        "iss": "https://login.elixir-czech.org/oidc/",
        "exp": expiry_time,
        "aud": "audience",
        "sub": "someone@somewhere.se",
        "scope": " ".join(GA4GH_SCOPES),
    }
    return claims


@pytest.fixture
def pem():
    """Test pem to include in the key
    https://python-jose.readthedocs.io/en/latest/jwk/index.html#examples
    """
    pem = {
        "kty": "oct",
        "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
        "use": "sig",
        "alg": "HS256",
        "k": "hJtXIZ2uSN5kbQfbtTNWbpdmhkV8FJG-Onbc6mxCcYg",
    }
    return pem


@pytest.fixture
def api_req_headers(api_user):
    """returns request headers for using the add and delete api with a valid token"""
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": api_user["token"],
    }
    return headers


@pytest.fixture
def api_user():
    """returns a test api user containing an auth token"""
    user = {
        "_id": "test_user",
        "name": "Test API user",
        "description": "Test API user description",
        "url": "https://testuser.se/",
        "created": "2021-01-11T09:31:15.450Z",
        "token": "6a7cbc6c-17d5-46bb-8671-709a186498f7",
    }
    return user


@pytest.fixture
def header():
    """Token header"""
    header = {
        "jku": "http://scilifelab.se/jkw",
        "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
        "alg": "HS256",
    }
    return header


@pytest.fixture
def test_token(header, payload, pem):
    """Generate and return JWT based on a demo private key"""
    token = jwt.encode(header, payload, pem)
    return token.decode("utf-8")


@pytest.fixture
def expired_token(header, pem):
    """Returns an expired token"""

    expiry_time = round(time.time()) - 60
    claims = {
        "iss": "https://login.elixir-czech.org/oidc/",
        "exp": expiry_time,
        "aud": "audience",
        "sub": "someone@somewhere.se",
    }
    token = jwt.encode(header, claims, pem)
    return token.decode("utf-8")


@pytest.fixture
def wrong_issuers_token(header, pem):
    """Returns a token with issuers different from those in the public key"""

    expiry_time = round(time.time()) + 60
    claims = {
        "iss": "wrong_issuers",
        "exp": expiry_time,
        "aud": "audience",
        "sub": "someone@somewhere.se",
    }

    token = jwt.encode(header, claims, pem)
    return token.decode("utf-8")


@pytest.fixture
def no_claims_token(header, pem):
    """Returns a token, with no claims"""

    claims = {}

    token = jwt.encode(header, claims, pem)
    return token.decode("utf-8")


@pytest.fixture
def registered_access_passport_info(header, pem):
    """Returns a JWT mocking a user identity with registered access permission on a dataset"""

    passport = {
        "ga4gh_visa_v1": {
            "type": "ControlledAccessGrants",
            "asserted": 1549640000,
            "value": "https://scilife-beacon/datasets/registered_ds",
        }
    }
    passport_info = [jwt.encode(header, passport, pem).decode("utf-8")]

    return passport_info


@pytest.fixture
def bona_fide_passport_info(header, pem):
    """Returns a JWT mocking a bona fide user (has access over controlled datasets)"""

    passports = [
        {
            "ga4gh_visa_v1": {
                "type": "AcceptedTermsAndPolicies",
                "value": "https://doi.org/10.1038/s41431-018-0219-y",
            }
        },
        {
            "ga4gh_visa_v1": {
                "type": "ResearcherStatus",
            }
        },
    ]
    passport_info = [jwt.encode(header, passport, pem).decode("utf-8") for passport in passports]

    return passport_info
