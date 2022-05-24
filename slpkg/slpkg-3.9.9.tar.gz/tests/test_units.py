import unittest
from slpkg.sizes import units


class TetsUnits(unittest.TestCase):

    def test_units(self):
        """Testing the units metrics
        """
        self.assertCountEqual((["Kb", "Kb"], [100, 100]),
                              units(["100"], ["100"]))
        self.assertCountEqual((["Mb", "Mb"], [1000, 1000]),
                              units(["1024000"], ["1024000"]))
        self.assertCountEqual((["Gb", "Gb"], [976.56, 976.56]),
                              units(["1024000000"], ["1024000000"]))


if __name__ == "__main__":
    unittest.main()
