#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import pytest

from ..object_access import ObjectAccess, ObjectAccessError, ObjectAccessMedium


class TestObjectAccess:
    def test_valid_object_access_1(self):

        url = "http://test"
        object_access = ObjectAccess(url=url)

        assert object_access.url == url
        assert object_access.to_dic() == {'url': 'http://test'}

    def test_valid_object_access_2(self):

        uri = "s3://test-bucket/abc"
        object_access = ObjectAccess(uri=uri,
                                     filename="this_file")

        assert object_access.uri == uri
        assert object_access.to_dic() == {'uri': uri,
                                          'filename': 'this_file'}

    def test_valid_object_access_3(self):
        object_access = ObjectAccess.from_dict(
            {'uri': "s3://test-bucket/abc",
             'medium': 's3',
             'filename': 'this_file'})
        assert object_access.uri == "s3://test-bucket/abc"
        assert object_access.medium == 's3'

    def test_invalid_object_access_1(self):
        with pytest.raises(ObjectAccessError):
            ObjectAccess()
