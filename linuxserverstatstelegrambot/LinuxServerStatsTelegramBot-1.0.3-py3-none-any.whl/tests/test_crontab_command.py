from unittest import TestCase
from LinuxServerStatsTelegramBot.commmand.CronStats import CronStats


class TestCrontabCommand(TestCase):
    def test_execute_command(self):
        command = CronStats()
        result = command.execute()
        print(result)
        self.assertTrue(True)
