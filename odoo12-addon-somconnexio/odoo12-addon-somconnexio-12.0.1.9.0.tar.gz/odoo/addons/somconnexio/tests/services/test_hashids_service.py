from ..sc_test_case import SCTestCase
from ...services.hashids_service import HashGetter, IDGetter
TEST_SALT = 'ABCD'


class HashIDsTests(SCTestCase):
    def test_convert_id_to_hash_and_back(self):
        id_to_hash = 19
        self.assertEqual(
            IDGetter(HashGetter(id_to_hash).get()).get(),
            id_to_hash
        )
