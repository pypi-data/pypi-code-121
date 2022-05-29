import unittest

from prep import number_systems, number_codes


class NumberSystemsWiki(unittest.TestCase):
    def setUp(self):
        self.number_systems_dict = number_systems[0]
        self.number_systems_tuple = number_systems[-1]
        self.number_codes_tuple = number_codes

    def test_number_systems_82(self):
        # get back 82 number systems
        self.assertEqual(len(self.number_systems_dict), 82)
        self.assertEqual(len(self.number_systems_tuple), 82)
        self.assertEqual(len(number_systems), 2)

    def test_number_systems_dict_convection(self):
        for nmd, nmt in zip(self.number_systems_dict, self.number_systems_tuple):
            # keys are the defined ones
            self.assertListEqual(['base', 'system', 'system_name'], list(nmd.keys()))
            # all values are strings
            self.assertEqual(
                True,
                all(type(value) == str for value in nmd.values())
            )
            # tuple type is integer
            self.assertEqual(type(nmt), int)

    def test_number_codes_length(self):
        # get 360 codes
        self.assertEqual(len(self.number_codes_tuple), 360)

    def test_number_codes_work(self):
        chr_s = list(filter(lambda c_: bool(c_), [chr(c) for c in self.number_codes_tuple]))
        self.assertEqual(len(chr_s), 360)


if __name__ == '__main__':
    unittest.main()
