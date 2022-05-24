import inspect, glob, os, datetime

from ...utils.api import route, Parameter

from ...libs import logs_lib, flask_lib, secure_lib

from ...models.main import AlphaException

from core import core

api = core.api
db = core.db
log = core.get_logger("api")


@route("/admin/key", parameters=[Parameter("key")], methods=["POST"])
def get_key():
    return secure_lib.magic_code(api["key"])


@route("/admin/logs/clear", methods=["GET"], admin=True, parameters=[])
def clear_logs():
    done = logs_lib.clear_logs(api)
    if not done:
        raise AlphaException("database")


@route(
    "/admin/logs",
    methods=["POST", "GET"],
    admin=True,
    parameters=[
        Parameter("page", required=True, ptype=int),
        Parameter("startDate", required=True),
        Parameter("endDate", required=True),
    ],
)
def admin_logs():
    page = int(api["page"])
    limit = page != 0
    return logs_lib.get_logs(
        start_date=api["startDate"],
        end_date=api["endDate"],
        useLimit=limit,
        pageForLimit=page,
    )


@route("/admin/process")
def get_process():
    import psutil

    output = {}
    # Iterate over all running process
    i = 0
    for proc in psutil.process_iter():
        if i > 10:
            break
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            processID = proc.pid
            if proc.memory_percent() > 0.01:
                print(processName, " ::: ", processID)
                output[processName] = proc.as_dict()
                i += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return output
