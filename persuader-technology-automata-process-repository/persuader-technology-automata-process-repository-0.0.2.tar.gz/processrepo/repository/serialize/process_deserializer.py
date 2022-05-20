from coreutility.collection.dictionary_utility import as_data

from processrepo.Process import Process, ProcessStatus


def deserialize_process(process) -> Process:
    name = as_data(process, 'name')
    instant = as_data(process, 'instant')
    status = ProcessStatus.parse(as_data(process, 'status'))
    return Process(name, instant, status)
