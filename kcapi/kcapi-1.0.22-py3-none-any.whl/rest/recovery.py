def add_failure_recovery(kc, fn):
    retry_count = 0
    def recovery(*args):
        resp = fn(*args)
        if resp.response.status_code == 401:
            kc.token = kc.token.refresh()
            return fn(*args)
        return resp

    return recovery

def add_failiure_recovery_decorator(kc):
    kc.create = add_failure_recovery(kc, kc.create)
    kc.update = add_failure_recovery(kc, kc.update)
    kc.findAll = add_failure_recovery(kc, kc.findAll)
    kc.get = add_failure_recovery(kc, kc.get)

    return kc