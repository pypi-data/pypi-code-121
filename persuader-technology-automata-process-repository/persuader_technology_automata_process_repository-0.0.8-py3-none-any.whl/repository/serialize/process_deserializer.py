from coreutility.collection.dictionary_utility import as_data

from processrepo.Process import Process, ProcessStatus
from processrepo.ProcessRunProfile import RunProfile


def deserialize_process(process) -> Process:
    market = as_data(process, 'market')
    name = as_data(process, 'name')
    instant = as_data(process, 'instant')
    run_profile = RunProfile.parse(as_data(process, 'run_profile'))
    status = ProcessStatus.parse(as_data(process, 'status'))
    return Process(market, name, instant, run_profile, status)
