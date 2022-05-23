from typing import Tuple, Any, Dict

from wai.test import AbstractTest
from wai.test.decorators import Test, ExceptionTest

from wai.common.meta import with_metadata, has_metadata, get_metadata


# Test class for holding meta-data
class TestClass:
    pass


class MetadataTest(AbstractTest):
    @classmethod
    def subject_type(cls):
        return with_metadata

    @classmethod
    def common_arguments(cls) -> Tuple[Tuple[object, str, int], Dict[str, Any]]:
        return (TestClass(), "test_key", 33), {}

    @Test
    def default(self, subject: TestClass):
        self.assertTrue(has_metadata(subject, "test_key"))
        self.assertEqual(get_metadata(subject, "test_key"), 33)

    @ExceptionTest(KeyError)
    def get_missing_key(self, subject: TestClass):
        get_metadata(subject, "missing")
