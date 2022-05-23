import unittest

from backend.dice_package.dice import RollableDie


class TestDie(unittest.TestCase):
    def setUp(self):
        self.die = RollableDie()

    def test_upper(self):
        self.assertEqual(self.die.sides, 6)
