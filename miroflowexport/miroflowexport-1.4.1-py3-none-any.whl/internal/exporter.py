import datetime

import openpyxl as xl

from miroflowexport import version
from miroflowexport.internal import excelcolumns
from miroflowexport.internal.excelcolumns import *
from miroflowexport.internal.versions import common

from miroflowexport.internal.versions import version_0
from miroflowexport.internal.versions import version_1

def metadata_from_excel(log, path):
    return common.metadata_from_excel(log, path)

class TaskUpdater:

    def __init__(self, log):
        self._log = log
        self._tasks_by_id = {}

    def update_tasks(self, tasks_by_id, source_tasks_by_id):
        if not source_tasks_by_id:
            self._log.debug("No tasks given that can serve as source of a task update.")
            return True

        for id in tasks_by_id.keys():
            if not id in source_tasks_by_id.keys():
                continue

            task = tasks_by_id[id]
            source = source_tasks_by_id[id]

            self._log.debug("Updating task '{}' ...".format(id))
            task.set_name(source.name())
            task.set_progress(source.progress())
            task.set_costs(source.costs())
            if source.start() >= task.earliest_start():
                if source.start() >= task.latest_finish():
                    task.set_start(task.latest_finish())
                else:
                    task.set_start(source.start())

        self._tasks_by_id = tasks_by_id
        
        return True

    def get_tasks(self):
        return self._tasks_by_id


class ExcelExporter:

    def __init__(self, log, path_to_excel):
        self._log = log
        self._path_to_excel = path_to_excel

    def export_tasks(self, tasks_dict, date_offset, granularity, colors = False):
        self._log.info("Starting export of tasks to '{}' ...".format(self._path_to_excel))
        success = version_1.tasks_to_excel(
            self._log,
            tasks_dict,
            path = self._path_to_excel,
            sheet_tasks = excelcolumns.DEFAULT_SHEET_TASKS,
            sheet_meta = excelcolumns.DEFAULT_SHEET_META,
            version = version,
            date_offset = date_offset,
            horizon_granularity = granularity,
            colors = colors,
        )
        if success:
            self._log.info("Finished export to '{}'.".format(self._path_to_excel))
        else:
            self._log.error("Exporting tasks to '{}' failed.".format(self._path_to_excel))
        return success

class ExcelImporter:

    def __init__(self, log, path_to_excel):
        self._log = log
        self._path_to_excel = path_to_excel
        self._version = None
        self._date_offset = datetime.date.today()
        self._tasks_dict = {}
        self._successful_import = False

    def import_from_excel(self):
        self._successful_import = False
        self._log.info("Starting import of tasks from '{}' ...".format(self._path_to_excel))
        date_offset, version = metadata_from_excel(self._log, self._path_to_excel)
        self._version = version
        if version == None:
            self._log.warning("Cannot find version information in Excel file, trying old-school import ...")
            success, tasks_dict = version_0.tasks_from_excel(self._log, self._path_to_excel)
            if not success:
                self._log.error("Importing tasks from '{}' failed.".format(self._path_to_excel))
                return False

            self._tasks_dict = tasks_dict
            self._successful_import = True
            return True

        self._date_offset = date_offset
        major = version[0]
        if major != 1:
            self._log.error("Found miroflow version {} in Excel, but I do not have a supporting importer. I quit import.".format(version))
            return False

        self._log.info("Found miroflowexport version of {} indicated in Excel, trying import ...".format(version))
        success, tasks_dict = version_1.tasks_from_excel(self._log, self._path_to_excel)
        if not success:
            self._log.error("Importing tasks from {} failed.".format(self._path_to_excel))
            return False

        num_tasks = len(tasks_dict.keys())
        self._log.info("Imported {} tasks from '{}'.".format(num_tasks, self._path_to_excel))
        self._tasks_dict = tasks_dict
        self._successful_import = True
        return True

    def get_version(self):
        if not self._successful_import:
            self._log.error("No Excel import run, there is no version information yet. Run an Excel import first.")
        return self._version

    def get_date_offset(self):
        if not self._successful_import:
            self._log.error("No Excel import run, there is no version information yet. Run an Excel import first.")
        return self._date_offset

    def get_tasks(self):
        if not self._successful_import:
            self._log.error("No Excel import run, there are no tasks yet. Run an Excel import first.")
        return self._tasks_dict

if __name__ == "__main__":
    wb = xl.load_workbook("tmp/export.xlsx")
    ws = wb.active

    col_progress = ws.column_dimensions['J']
    print("Number format: '{}'".format(col_progress.number_format))