import unittest
from sdap.data_access.index.spatial.GoogleS2 import S2Key

class S2KeyTestCase(unittest.TestCase):
    def test_get_id(self):
        s2_id = 13168525310431330304
        key = S2Key(s2_id) # key is already level 3
        key_level_3 = key.get_id(level=3)
        assert s2_id == key_level_3



if __name__ == '__main__':
    unittest.main()
