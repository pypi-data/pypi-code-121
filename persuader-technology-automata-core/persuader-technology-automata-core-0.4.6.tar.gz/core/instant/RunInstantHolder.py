from datetime import datetime, timezone


class RunInstantHolder:
    run_instant = None

    @staticmethod
    def initialize(run_instant=None):
        if run_instant is not None:
            RunInstantHolder.run_instant = run_instant
        else:
            RunInstantHolder.run_instant = datetime.now(timezone.utc)

    @staticmethod
    def numeric_run_instance(delimiter='.'):
        if type(RunInstantHolder.run_instant) is datetime:
            numeric_value = RunInstantHolder.run_instant.timestamp()
            return numeric_value if delimiter == '.' else int(str(numeric_value).replace('.', delimiter))
        else:
            return RunInstantHolder.run_instant
