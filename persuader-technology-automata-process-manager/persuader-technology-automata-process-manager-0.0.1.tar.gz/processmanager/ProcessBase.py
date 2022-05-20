from processrepo.Process import ProcessStatus
from processrepo.repository.ProcessRepository import ProcessRepository

from processmanager.reporter.ProcessReporter import ProcessReporter


class ProcessBase:

    def __init__(self, options, process_name):
        self.options = options
        self.process_name = process_name
        self.process_state = ProcessStatus.STOPPED
        self.process_reporter = self.__init_process_reporter()

    def __init_process_reporter(self):
        process_repository = ProcessRepository(self.options)
        return ProcessReporter(process_repository)

    def running(self):
        self.process_state = ProcessStatus.RUNNING
        self.report_process_status()

    def error(self):
        self.process_state = ProcessStatus.ERROR
        self.report_process_status()

    def stopped(self):
        self.process_state = ProcessStatus.STOPPED
        self.report_process_status()

    def report_process_status(self):
        self.process_reporter.report(self.process_name, self.process_state)
