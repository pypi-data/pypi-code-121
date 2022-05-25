from time import sleep

import schedule
from processrepo.ProcessRunProfile import RunProfile

from processmanager.ProcessRunner import ProcessRunner
from processmanager.termination.GracefulTermination import GracefulTermination


class ScheduledProcess(ProcessRunner):

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
            schedule.every().day.at('06:00').do(self.run)
        else:
            schedule.every(1).second.do(self.run)

    def start_process_schedule(self):
        self.log.info(f'START Scheduling {self.market} - {self.process_name}')
        termination = GracefulTermination()
        while not termination.kill_now:
            schedule.run_pending()
            sleep(1)
        self.stop_process_schedule()

    def stop_process_schedule(self):
        self.log.info(f'STOP Scheduling {self.market} - {self.process_name}')
        self.process_stopped()
