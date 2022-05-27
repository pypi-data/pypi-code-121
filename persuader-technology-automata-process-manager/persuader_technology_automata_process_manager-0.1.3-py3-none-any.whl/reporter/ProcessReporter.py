import logging

from coreutility.date_utility import get_utc_timestamp
from processrepo.Process import ProcessStatus, Process
from processrepo.ProcessRunProfile import RunProfile
from processrepo.repository.ProcessRepository import ProcessRepository


class ProcessReporter:

    def __init__(self, repository: ProcessRepository):
        self.log = logging.getLogger(__name__)
        self.repository = repository

    def report(self, process_name, process_version, market, run_profile: RunProfile, status: ProcessStatus):
        instant = get_utc_timestamp()
        process = Process(market, process_name, process_version, instant, run_profile, status)
        self.log.debug(f'Reporting process:[{process}]')
        self.repository.store(process)
