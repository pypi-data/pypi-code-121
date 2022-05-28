# standard libraries
import logging
import unittest

# third party libraries
# None

# local libraries
from nion.utils import Observable


class TestObservableClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_observable(self) -> None:
        Observable.Observable()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
