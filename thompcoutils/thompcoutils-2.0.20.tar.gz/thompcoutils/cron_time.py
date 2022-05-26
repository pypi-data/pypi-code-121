from thompcoutils.test_utils import assert_test
import datetime

_debug = False
_now_time = None


def _now():
    if _debug:
        return _now_time
    else:
        return datetime.datetime.now()


class CronTimeException(Exception):
    pass


class CronTime:

    def __init__(self, day_of_week=0, month=0, day_of_month=0, hour=0, minute=0):
        self.day_of_week = day_of_week
        self.month = month
        self.day_of_month = day_of_month
        self.hour = hour
        self.minute = minute

    def __str__(self):
        return CronTime.strfcrontime(self, '%w %d %m %H %M')

    # allowed characters are:
    # %w single digit weekday (0=Sunday)
    # %d two digit day of the month
    # %m two digit month
    # %H two digit hour
    # %M two digit minute
    @staticmethod
    def strfpcrontime(source_string, format_string):
        cron_time = CronTime()
        j = 0
        i = 0
        for r in range(0, len(format_string)):
            if i > len(format_string) - 1:
                break
            if format_string[i] == '%':
                fmt = format_string[i+1]
                if fmt == 'w':
                    cron_time.day_of_week = int(source_string[j:j+1])
                    i += 1
                elif fmt == 'm':
                    cron_time.month = int(source_string[j:j+2])
                elif fmt == 'd':
                    cron_time.day_of_month = int(source_string[j:j+2])
                elif fmt == 'H':
                    cron_time.hour = int(source_string[j:j+2])
                elif fmt == 'M':
                    cron_time.minute = int(source_string[j:j+2])
                else:
                    raise CronTimeException("%{} not recognised as a CronTime format".format(fmt))
            i += 1
            j += 1
        return cron_time

    def strfcrontime(self, format_string):
        rtn = ''
        i = 0
        for y in range(0, len(format_string)):
            if i > len(format_string) - 1:
                break
            if format_string[i] == '%':
                fmt = format_string[i+1]
                if fmt == 'w':
                    rtn += '{:1d}'.format(self.day_of_week)
                elif fmt == 'm':
                    rtn += '{:02d}'.format(self.month)
                elif fmt == 'd':
                    rtn += '{:02d}'.format(self.day_of_month)
                elif fmt == 'H':
                    rtn += '{:02d}'.format(self.hour)
                elif fmt == 'M':
                    rtn += '{:02d}'.format(self.minute)
                else:
                    raise CronTimeException("%{} not recognised as a CronTime format".format(fmt))
                i += 1
            else:
                rtn += format_string[i]
            i += 1
        return rtn

    def triggered(self):
        minute = False
        hour = False
        day = False
        month = False
        day_of_week = False

        if self.minute == 0:
            minute = True
        elif _now().minute == self.minute:
            minute = True

        if self.hour == 0:
            hour = True
        elif _now().hour == self.hour:
            hour = True

        if self.day_of_month == 0:
            day = True
        elif _now().day == self.day_of_month:
            day = True

        if self.month == 0:
            month = True
        elif _now().month == self.month:
            month = True

        if self.day_of_week == 0:
            day_of_week = True
        elif _now().weekday() == self.day_of_week:
            day_of_week = True

        return minute and hour and day and month and day_of_week


def _test_crontime():
    format_string = '%w %d %m %H %M'
    source_string = '1 02 03 04 05'
    cron_time = CronTime.strfpcrontime(source_string, format_string)
    assert_test(cron_time.day_of_week == 1)
    assert_test(cron_time.day_of_month == 2)
    assert_test(cron_time.month == 3)
    assert_test(cron_time.hour == 4)
    assert_test(cron_time.minute == 5)
    print(cron_time)
    test_string = cron_time.strfcrontime(format_string)
    assert_test(test_string == source_string)


if __name__ == "__main__":
    _test_crontime()
