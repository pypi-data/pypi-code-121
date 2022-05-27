import os
from pathlib import Path

import pytest

from tests.fixtures import VCR
from unicef_security.graph import Synchronizer


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/test_token.yml'))
@pytest.mark.skipif(os.environ.get("CIRCLECI") == "true", reason="Skip in CirlceCI")
def test_token():
    s = Synchronizer()
    assert s.access_token


@pytest.mark.skipif(os.environ.get("CIRCLECI") == "true", reason="Skip in CirlceCI")
@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/test_user_data.yml'))
def test_user_data():
    s = Synchronizer()
    info = s.get_user('sapostolico@unicef.org')
    assert info['displayName']
    assert info['givenName']
    assert info['id']
    assert sorted(info.keys()) == sorted(['@odata.context', 'id', 'businessPhones',
                                          'displayName', 'givenName', 'jobTitle',
                                          'mail', 'mobilePhone', 'officeLocation',
                                          'preferredLanguage', 'surname',
                                          'userPrincipalName'])
