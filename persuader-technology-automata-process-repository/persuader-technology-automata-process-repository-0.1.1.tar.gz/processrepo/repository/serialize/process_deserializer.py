from coreutility.collection.dictionary_utility import as_data

from processrepo.Process import Process, ProcessStatus
from processrepo.ProcessRunProfile import RunProfile


def deserialize_process(process) -> Process:
    if process is not None:
        market = as_data(process, 'market')
        name = as_data(process, 'name')
        version = as_data(process, 'version')
        instant = as_data(process, 'instant')
        run_profile = RunProfile.parse(as_data(process, 'run_profile'))
        status = ProcessStatus.parse(as_data(process, 'status'))
        return Process(market, name, version, instant, run_profile, status)
