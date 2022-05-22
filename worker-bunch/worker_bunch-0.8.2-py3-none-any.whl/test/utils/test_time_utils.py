import datetime
import unittest

from tzlocal import get_localzone

from worker_bunch.utils.time_utils import TimeUtils


class TestTimeUtils(unittest.TestCase):

    def test_is_cron_time_minute(self):
        cron = "2 * * * *"

        t = datetime.datetime(2022, 1, 30, 10, 0, 30, tzinfo=get_localzone())

        self.assertFalse(TimeUtils.hits_cron_time(cron, t))
        self.assertFalse(TimeUtils.hits_cron_time(cron, t.replace(minute=1)))
        self.assertFalse(TimeUtils.hits_cron_time(cron, t.replace(minute=3)))
        self.assertFalse(TimeUtils.hits_cron_time(cron, t.replace(minute=4)))

        self.assertTrue(TimeUtils.hits_cron_time(cron, t.replace(minute=2)))
        self.assertTrue(TimeUtils.hits_cron_time(cron, t.replace(minute=2, second=0)))

    def test_is_cron_time_per_minute(self):
        cron = "*/5 * * * *"
        t = datetime.datetime(2022, 1, 30, 10, 0, 30, tzinfo=get_localzone())

        count = 0
        for i in range(0, 60):
            if TimeUtils.hits_cron_time(cron, t.replace(minute=i)):
                count += 1

        self.assertEqual(count, 12)

    def test_is_cron_time_hour_range(self):
        cron = "1 10-15 * * *"
        t = datetime.datetime(2022, 1, 31, 10, 1, 30, tzinfo=get_localzone())

        count = 0
        for i in range(0, 24):
            if TimeUtils.hits_cron_time(cron, t.replace(hour=i)):
                count += 1

        self.assertEqual(count, 6)

    def test_is_cron_time_hour_list(self):
        cron = "1 10,11,12,13,14,15 * * *"
        t = datetime.datetime(2022, 1, 29, 10, 1, 30, tzinfo=get_localzone())

        count = 0
        for i in range(0, 24):
            if TimeUtils.hits_cron_time(cron, t.replace(hour=i)):
                count += 1

        self.assertEqual(count, 6)

    def test_cron_every_hour(self):
        now = TimeUtils.now()
        for i in range(1, 10000):
            result_hit = TimeUtils.hits_cron_time("0 0 * * *", now)
            expected_hit = now.hour == 0 and now.minute == 0
            self.assertEqual(result_hit, expected_hit)
            now = now + datetime.timedelta(seconds=45, microseconds=434)
