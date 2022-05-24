import logging

from processrepo.Process import ProcessStatus
from processrepo.repository.ProcessRepository import ProcessRepository
from processrepo.repository.ProcessRunProfileRepository import ProcessRunProfileRepository

from processmanager.error.ProcessRunProfileMissing import ProcessRunProfileMissing
from processmanager.reporter.ProcessReporter import ProcessReporter


class ProcessBase:

    def __init__(self, options, market, process_name):
        self.log = logging.getLogger(__name__)
        self.options = options
        self.market = market
        self.process_name = process_name
        self.process_state = ProcessStatus.INITIALIZED
        self.process_reporter = self.init_process_reporter()
        self.process_run_profile = self.init_process_run_profile()
        self.report_process_status()

    def init_process_reporter(self):
        process_repository = ProcessRepository(self.options)
        return ProcessReporter(process_repository)

    def init_process_run_profile(self):
        process_run_profile_repository = ProcessRunProfileRepository(self.options)
        process_run_profile = process_run_profile_repository.retrieve(self.process_name, self.market)
        if process_run_profile is None:
            self.process_error()
            self.log.warning(f'Run profile missing for market:{self.market} process name:{self.process_name}')
            raise ProcessRunProfileMissing(f'Run profile missing for market:{self.market} process name:{self.process_name}')
        return process_run_profile.run_profile

    def process_running(self):
        self.process_state = ProcessStatus.RUNNING
        self.report_process_status()

    def process_error(self):
        self.process_state = ProcessStatus.ERROR
        self.report_process_status()

    def process_stopped(self):
        self.process_state = ProcessStatus.STOPPED
        self.report_process_status()

    def report_process_status(self):
        self.process_reporter.report(self.process_name, self.market, self.process_run_profile, self.process_state)
