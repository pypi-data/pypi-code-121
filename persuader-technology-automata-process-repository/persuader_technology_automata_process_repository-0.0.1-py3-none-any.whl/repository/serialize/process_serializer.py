from processrepo.Process import Process


def serialize_process(process: Process) -> dict:
    serialized = {
        'name': process.name,
        'instant': process.instant,
        'status': process.status.value
    }
    return serialized
