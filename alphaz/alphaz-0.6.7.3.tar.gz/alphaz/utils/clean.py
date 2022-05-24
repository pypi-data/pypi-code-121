import datetime

from ..models.database.main_definitions import FilesProcess, Processes


def clean(days=360):
    from core import core

    core.db.delete(
        FilesProcess,
        filters=[
            FilesProcess.update_date
            < datetime.datetime.now() + datetime.timedelta(days=days),
        ],
    )

    Processes
