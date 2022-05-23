from email.message import Message
import sys
import datetime


class PrintInfo():
    def __init__(self, name):
        super(PrintInfo, self).__init__()
        self.name = name

    def start(self):
        self.start_time = datetime.datetime.now()
        print_info("Running %s..." % (self.name))

    def end(self):
        self.end_time = datetime.datetime.now()
        execution_time = round(
            (self.end_time - self.start_time).total_seconds() * 1000)
        print_info(
            "Running %s completed, took %sms" % (self.name, execution_time))
        print()


def print_info(message):
    print('[INFO] %s' % message)


def print_error(message):
    print('\33[31m' + '[ERROR] %s' % message + '\033[0m')
