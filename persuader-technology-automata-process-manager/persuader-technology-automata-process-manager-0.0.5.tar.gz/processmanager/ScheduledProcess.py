from time import sleep

import schedule
from processrepo.ProcessRunProfile import RunProfile

from processmanager.ProcessBase import ProcessBase


class ScheduledProcess(ProcessBase):

    def __init__(self, options, market, process_name):
        super().__init__(options, market, process_name)
        self.schedule_to_process_run_profile()

    def schedule_to_process_run_profile(self):
        self.log.info(f'Scheduling process to {self.process_run_profile}')
        if self.process_run_profile == RunProfile.MINUTE:
            schedule.every().minute.do(self.run)
        elif self.process_run_profile == RunProfile.HOUR:
            schedule.every().hour.do(self.run)
        elif self.process_run_profile == RunProfile.DAY:
            schedule.every().day.at('07:00').do(self.run)
        else:
            schedule.every(1).second.do(self.run)

    @staticmethod
    def start_process_schedule():
        while True:
            schedule.run_pending()
            sleep(1)
