import datetime
import time

import pycron
from tzlocal import get_localzone


class TimeUtils:

    @classmethod
    def now(cls, no_ms=False) -> datetime.datetime:
        """overwrite/mock in test"""
        now = datetime.datetime.now(tz=get_localzone())
        if no_ms:
            now = now.replace(microsecond=0)
        return now

    @classmethod
    def diff_seconds(cls, reference: datetime.datetime):
        return (cls.now() - reference).total_seconds()

    @classmethod
    def sleep(cls, seconds: float) -> int:
        time.sleep(seconds)
        return seconds

    @classmethod
    def hits_cron_time(cls, cron: str, now: datetime.datetime = None):
        """
        Returns True is the cron is triggering right `now`
        """
        now = now if now is not None else cls.now()
        return pycron.is_now(cron, now)

    @classmethod
    def is_cron_time_syntax(cls, cron: str):
        """
        Checks if the string is a proper cron syntax
        """
        try:
            cls.hits_cron_time(cron)  # result down not matter here
            return True
        except ValueError:
            return False
