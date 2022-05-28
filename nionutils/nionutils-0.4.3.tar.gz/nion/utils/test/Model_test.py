# standard libraries
import asyncio
import contextlib
import logging
import typing
import unittest
import weakref

# third party libraries
# None

# local libraries
from nion.utils import Model
from nion.utils import Stream


@contextlib.contextmanager
def event_loop_context() -> typing.Iterator[asyncio.AbstractEventLoop]:
    event_loop = asyncio.new_event_loop()
    yield event_loop
    event_loop.stop()
    event_loop.run_forever()
    event_loop.close()


class TestModelClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_refcounts(self) -> None:
        with event_loop_context() as event_loop:
            # property model
            model = Model.PropertyModel[int](0)
            model_ref = weakref.ref(model)
            del model
            self.assertIsNone(model_ref())
            # func stream model (ugh)
            model2 = Model.FuncStreamValueModel(Stream.ValueStream(lambda: None), event_loop)
            model_ref2 = weakref.ref(model2)
            del model2
            self.assertIsNone(model_ref2())
            # stream value model
            model3 = Model.StreamValueModel(Stream.ValueStream(0))
            model_ref3 = weakref.ref(model3)
            del model3
            self.assertIsNone(model_ref3())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
