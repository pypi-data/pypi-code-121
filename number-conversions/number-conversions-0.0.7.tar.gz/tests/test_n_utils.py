import unittest

import n_utils


class UtilsCase(unittest.TestCase):
    def test_recurring_patterns(self):
        self.assertEqual('4', n_utils.find_recurring_pattern('444444'))
        self.assertEqual('geeksforgeeks', n_utils.find_recurring_pattern('geeksforgeeksgeeksforgeeksgeeksforgeeks'))
        self.assertEqual('124', n_utils.find_recurring_pattern('1232124124124124'))
        self.assertEqual('muremwav', n_utils.find_recurring_pattern('mynameismuremwavmuremwavmuremwavmuremwa'))
        self.assertEqual('3', n_utils.find_recurring_pattern('343333333'))

    def test_assurances_standard_base(self):
        self.assertTrue(n_utils.ensure_base_is_standard(2))
        self.assertTrue(n_utils.ensure_base_is_standard(23))
        self.assertTrue(n_utils.ensure_base_is_standard(64))
        self.assertTrue(n_utils.ensure_base_is_standard(8))
        self.assertTrue(n_utils.ensure_base_is_standard(10))
        self.assertTrue(n_utils.ensure_base_is_standard(16))
        self.assertTrue(n_utils.ensure_base_is_standard(216))
        self.assertTrue(n_utils.ensure_base_is_standard(360))

        self.assertFalse(n_utils.ensure_base_is_standard(259))
        self.assertFalse(n_utils.ensure_base_is_standard(63))
        self.assertFalse(n_utils.ensure_base_is_standard(71))
        self.assertFalse(n_utils.ensure_base_is_standard(101))
        self.assertFalse(n_utils.ensure_base_is_standard(301))
        self.assertFalse(n_utils.ensure_base_is_standard(214))
        self.assertFalse(n_utils.ensure_base_is_standard(359))

    def test_base_limits(self):
        self.assertTrue(n_utils.base_limits('AE', 16))
        self.assertTrue(n_utils.base_limits('AG', 30))
        self.assertTrue(n_utils.base_limits('AB', 12))
        self.assertTrue(n_utils.base_limits('10', 10))

        self.assertFalse(n_utils.base_limits('G4', 16))
        self.assertFalse(n_utils.base_limits('G4', 10))
        self.assertFalse(n_utils.base_limits('02', 2))
        self.assertFalse(n_utils.base_limits('9', 8))

    def test_base_find(self):
        self.assertEqual('Undecimal', n_utils.base_find(11))
        self.assertEqual('Decimal', n_utils.base_find(10))
        self.assertEqual('Binary', n_utils.base_find(2))
        self.assertEqual('Trecentosexagesimal', n_utils.base_find(360))
        self.assertEqual('Enneaoctogesimal', n_utils.base_find(89))
        self.assertEqual('Trigesimal', n_utils.base_find(30))


if __name__ == '__main__':
    unittest.main()
