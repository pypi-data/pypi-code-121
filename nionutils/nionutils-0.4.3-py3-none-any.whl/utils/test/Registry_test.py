# standard libraries
import logging
import unittest

# local libraries
from nion.utils import Registry


class TestConverter(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_registering_same_component_with_different_types_succeeds(self) -> None:
        o = object()
        Registry.register_component(o, {"one", "two"})
        Registry.register_component(o, {"three"})
        self.assertEqual(o, Registry.get_component("one"))
        self.assertEqual(o, Registry.get_component("three"))
        Registry.unregister_component(o, {"three"})
        self.assertEqual(o, Registry.get_component("one"))
        self.assertIsNone(Registry.get_component("three"))
        Registry.unregister_component(o)
        self.assertIsNone(Registry.get_component("one"))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
