# standard libraries
import copy
import logging
import typing
import unittest
import weakref

# third party libraries
# None

# local libraries
from nion.utils import StructuredModel
from nion.utils import Recorder


class TestRecorderClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_refcounts(self) -> None:
        # create the model
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        record = StructuredModel.define_record("R", [x_field, y_field])
        array = StructuredModel.define_array(record)
        schema = StructuredModel.define_record("A", [StructuredModel.define_field("a", array)])
        model = StructuredModel.build_model(schema, value={"a": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]})
        # create recorder
        r = Recorder.Recorder(model)
        # check recorder refcount
        r_ref = weakref.ref(r)
        del r
        self.assertIsNone(r_ref())

    @typing.no_type_check
    def test_refcounts_after_record_and_apply(self) -> None:
        # create the model
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        record = StructuredModel.define_record("R", [x_field, y_field])
        array = StructuredModel.define_array(record)
        schema = StructuredModel.define_record("A", [StructuredModel.define_field("a", array)])
        model = StructuredModel.build_model(schema, value={"a": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]})
        # create recorder
        r = Recorder.Recorder(model)
        # change the model
        model_copy = copy.deepcopy(model)
        model.a[1].x = 33
        del model.a[0]
        model.a.insert(1, StructuredModel.build_model(record, value={"x": -1, "y": -2}))
        # confirm changes
        self.assertEqual(33, model.a[0].x)
        self.assertEqual(-2, model.a[1].y)
        # confirm copy
        self.assertEqual(1, model_copy.a[0].x)
        self.assertEqual(4, model_copy.a[1].y)
        r.apply(model_copy)
        self.assertEqual(33, model_copy.a[0].x)
        self.assertEqual(-2, model_copy.a[1].y)
        # check recorder refcount
        r_ref = weakref.ref(r)
        del r
        self.assertIsNone(r_ref())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
