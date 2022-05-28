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


class TestStreamClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_refcounts(self) -> None:
        with event_loop_context() as event_loop:
            # map stream, value stream
            stream = Stream.MapStream(Stream.ValueStream(0), lambda x: x)
            stream_ref = weakref.ref(stream)
            del stream
            self.assertIsNone(stream_ref())
            # combine stream
            stream2 = Stream.CombineLatestStream[typing.Any, typing.Any]([Stream.ValueStream(0), Stream.ValueStream(0)])
            stream_ref2 = weakref.ref(stream2)
            del stream2
            self.assertIsNone(stream_ref2())
            # debounce
            stream3 = Stream.DebounceStream(Stream.ValueStream(0), 0.0, event_loop)
            stream_ref3 = weakref.ref(stream3)
            del stream3
            self.assertIsNone(stream_ref3())
            # sample
            stream4 = Stream.SampleStream(Stream.ValueStream(0), 0.0, event_loop)
            stream_ref4 = weakref.ref(stream4)
            del stream4
            self.assertIsNone(stream_ref4())
            # property changed event stream
            stream5 = Stream.PropertyChangedEventStream[typing.Any](Model.PropertyModel(0), "value")
            stream_ref5 = weakref.ref(stream5)
            del stream5
            self.assertIsNone(stream_ref5())
            # optional stream
            stream6 = Stream.OptionalStream(Stream.ValueStream(0), lambda x: True)
            stream_ref6 = weakref.ref(stream6)
            del stream6
            self.assertIsNone(stream_ref6())
            # value stream action
            action = Stream.ValueStreamAction(Stream.ValueStream(0), lambda x: None)
            action_ref = weakref.ref(action)
            del action
            self.assertIsNone(action_ref())
            # value change stream
            stream7 = Stream.ValueChangeStream(Stream.ValueStream(0))
            stream_ref7 = weakref.ref(stream7)
            del stream7
            self.assertIsNone(stream_ref7())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
