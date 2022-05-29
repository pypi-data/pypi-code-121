from TDhelper.Scheduler.interface import InterfaceScheduler


class example_scheduler(InterfaceScheduler):
    def __init__(self, _config):
        self._name = _config["name"]
        self._plug = _config["_plugin"]
        self._taskType = _config["taskType"]
        self._startTime = _config["startTime"]
        self._sleep = _config["sleep"]
        super().__init__(
            self._name, self._plug, self._taskType, self._startTime, self._sleep
        )

    async def run(self, *args, **kw):
        try:
            for i in range(0, 5000):
                pass
            return True, {"code": 200, "msg": "", "result": "Example."}
        except Exception as e:
            return False, {"code": 500, "msg": e, "result": "Example."}
