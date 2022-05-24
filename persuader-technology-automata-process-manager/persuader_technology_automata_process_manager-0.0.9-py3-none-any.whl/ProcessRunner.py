import sys
import traceback

from processrepo.Process import ProcessStatus

from processmanager.ProcessBase import ProcessBase


class ProcessRunner(ProcessBase):

    def __init__(self, options, market, process_name):
        super().__init__(options, market, process_name)

    def should_run_process(self) -> bool:
        if self.intervene_process() is True:
            return False
        if self.process_state in [ProcessStatus.RUNNING, ProcessStatus.ERROR]:
            return False
        return True

    def run(self):
        if self.should_run_process():
            try:
                self.process_running()
                self.process_to_run()
                self.process_stopped()
            except Exception as err:
                exc_info = sys.exc_info()
                self.log.warning(f'Process has an error:[{type(err)}] "{err}"')
                self.process_error()
                traceback.print_exception(*exc_info)

    # override, by defining the process to run
    def process_to_run(self):
        pass

    # any condition resulting in True, will prevent/intervene the process
    def intervene_process(self) -> bool:
        return False
