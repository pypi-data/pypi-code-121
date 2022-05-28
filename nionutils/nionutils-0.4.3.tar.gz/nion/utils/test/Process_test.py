# standard libraries
import logging
import unittest

# third party libraries
# None

# local libraries
from nion.utils import Process


class TestObservableClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_process(self) -> None:
        ts = Process.TaskQueue()
        a = 0
        b = 0

        def aa() -> None:
            nonlocal a
            a += 1

        def bb() -> None:
            nonlocal b
            b += 1

        ts.put(aa)
        ts.put(aa)
        ts.put(bb)

        ts.perform_tasks()

        self.assertEqual(2, a)
        self.assertEqual(1, b)

        ts.put(aa)
        ts.clear_tasks()
        ts.put(aa)
        ts.put(bb)

        ts.perform_tasks()

        self.assertEqual(3, a)
        self.assertEqual(2, b)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
