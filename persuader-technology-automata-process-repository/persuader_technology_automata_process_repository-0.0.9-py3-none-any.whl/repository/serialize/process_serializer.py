from processrepo.Process import Process


def serialize_process(process: Process) -> dict:
    serialized = {
        'market': process.market,
        'name': process.name,
        'instant': process.instant,
        'run_profile': process.run_profile.value,
        'status': process.status.value
    }
    return serialized
