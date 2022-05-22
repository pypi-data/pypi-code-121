import __init__
import unittest
from TDhelper.Scheduler.service import SchedulerService

class TestScheduler(unittest.TestCase):
    def test_scheduler(self):
        SCHEDULER_SERVICE= SchedulerService("//data")


if __name__ == "__main__":
    unittest.main()
