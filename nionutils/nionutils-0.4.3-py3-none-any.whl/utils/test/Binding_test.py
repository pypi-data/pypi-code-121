# standard libraries
import logging
import typing
import unittest

# third party libraries
# None

# local libraries
import weakref

from nion.utils import Binding
from nion.utils import Event
from nion.utils import Geometry
from nion.utils import Model


class TupleModel:

    def __init__(self) -> None:
        self.__tuple: typing.Optional[typing.Tuple[typing.Any]] = None
        self.property_changed_event = Event.Event()

    @property
    def tuple(self) -> typing.Optional[typing.Tuple[typing.Any]]:
        return self.__tuple

    @tuple.setter
    def tuple(self, value: typing.Optional[typing.Tuple[typing.Any]]) -> None:
        self.__tuple = value
        self.property_changed_event.fire("tuple")


class TestBindingClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_property_binding_refcount(self) -> None:
        binding = Binding.PropertyBinding(Model.PropertyModel(0), "value")
        binding_ref = weakref.ref(binding)
        del binding
        self.assertIsNone(binding_ref())

    def test_property_attribute_binding_refcount(self) -> None:
        binding = Binding.PropertyAttributeBinding(Model.PropertyModel(Geometry.FloatPoint()), "value", "x")
        binding_ref = weakref.ref(binding)
        del binding
        self.assertIsNone(binding_ref())

    def test_tuple_property_binding_refcount(self) -> None:
        binding = Binding.TuplePropertyBinding(Model.PropertyModel((1, 2, 3)), "value", 1)
        binding_ref = weakref.ref(binding)
        del binding
        self.assertIsNone(binding_ref())

    def test_tuple_binding_pads_to_index_if_necessary(self) -> None:
        # this allows the source to more easily go from None to a partialy tuple None -> (3, None) -> (3, 4)
        source = typing.cast(typing.Any, TupleModel())
        self.assertEqual(None, source.tuple)
        binding0 = Binding.TuplePropertyBinding(source, "tuple", 0)
        binding2 = Binding.TuplePropertyBinding(source, "tuple", 2)
        binding0.update_source("abc")
        self.assertEqual(("abc", ), source.tuple)
        binding2.update_source("ghi")
        self.assertEqual(("abc", None, "ghi"), source.tuple)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
