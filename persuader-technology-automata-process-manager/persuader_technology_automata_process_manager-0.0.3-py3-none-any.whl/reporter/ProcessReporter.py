from coreutility.date_utility import get_utc_timestamp
from processrepo.Process import ProcessStatus, Process
from processrepo.repository.ProcessRepository import ProcessRepository


class ProcessReporter:

    def __init__(self, repository: ProcessRepository):
        self.repository = repository

    def report(self, process_name, market, status: ProcessStatus):
        instant = get_utc_timestamp()
        process = Process(market, process_name, instant, status)
        self.repository.store(process)
