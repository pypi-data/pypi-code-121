import json
import os
import time

import pandas as pd

from kamzik3 import DeviceError, SEP
from kamzik3.constants import *
from kamzik3.devices.deviceFileSync import DeviceFileSync
from kamzik3.snippets.snippetsDecorators import expose_method

UPDATE_INSERT_GROUPS = "Insert groups"
UPDATE_INSERT_ROW = "Insert row"
UPDATE_REMOVE_GROUP = "Remove group"
UPDATE_VALUE = "Update value"
UPDATE_REMOVE_ROW = "Remove row"


class DeviceSavedAttributes(DeviceFileSync):
    def _init_attributes(self):
        DeviceFileSync._init_attributes(self)
        self.create_attribute(ATTR_GROUPS, type=TYPE_ARRAY, readonly=True)
        attribute = self.create_attribute(ATTR_LAST_UPDATE, readonly=True)
        # We set min_broadcast_timeout to zero to make sure all messages are broadcast
        attribute.min_broadcast_timeout = 0

    def handle_configuration(self):
        start_at = time.time()
        self._config_commands()
        self._config_attributes()
        self.set_value(ATTR_FILEPATH, self.filepath)
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def set_filepath(self, value):
        """
        Set filepath for h5 source file.

        :param value:
        :type value: string
        """
        if not os.path.exists(value):
            try:
                hdf = pd.DataFrame(data={"Comment"})
                hdf.to_hdf(value, "default", format="table", complevel=1)
            except PermissionError as e:
                raise DeviceError(e)
        else:
            with pd.HDFStore(value) as hdf:
                self.set_value(ATTR_GROUPS, hdf.keys())

        with open(self.filepath, "rb") as fp:
            self.set_raw_value(ATTR_CONTENT, fp.read())

    @expose_method({"groups_data": "Dict with group definitions"})
    def insert_groups(self, groups_data):
        """
        Insert multiple groups into saved attributes file.

        Each group is defined by entry in dict.
        Key is path to group and value is header of table.
        Example of group:
        {"/Default/Sample": {"Color", "Comment", "X [Position][mm]", "Y [Position][mm]", "Yaw [Position][deg]"}}

        :param groups_data: dict {group_path_1: {Color, Time, Comment, Device [
         Attribute][Unit]}, group_path_n: {...}}
        :type groups_data: dict
        """
        for group, data in groups_data.items():
            df = pd.DataFrame(data, columns=list(data.keys()))
            df.to_hdf(self.filepath, key=group, format="table", complevel=1)
            self.set_value(
                ATTR_LAST_UPDATE,
                SEP.join((UPDATE_INSERT_GROUPS, json.dumps(groups_data))),
            )

        self.store_dataframe()
        with pd.HDFStore(self.filepath) as hdf:
            self.set_value(ATTR_GROUPS, hdf.keys())

    @expose_method({"groups_data": "Dict with group definitions"})
    def remove_group(self, group):
        with pd.HDFStore(self.filepath) as hdf:
            for group_path in self.get_value(ATTR_GROUPS):
                if group_path.startswith(f"/{group}/"):
                    hdf.remove(group_path)
            self.set_value(ATTR_LAST_UPDATE, SEP.join((UPDATE_REMOVE_GROUP, group)))
            self.set_value(ATTR_GROUPS, hdf.keys())

        self.store_dataframe()

    @expose_method(
        {"group": "Path to existing group", "data": "Row dict with attributes"}
    )
    def insert_row(self, group, data, position=0):
        """
        Insert new row into group specified by group path.

        :param group: group path
        :type group: string
        :param data: {row color, user comment, Value of attribute, ...}
        :type data: dict
        """
        df = pd.read_hdf(self.filepath, key=group)
        line = pd.DataFrame(data, index=[position])
        df2 = pd.concat([df.iloc[: position - 1], line, df.iloc[position - 1 :]])
        df2.reset_index(drop=True, inplace=True)
        df2.to_hdf(self.filepath, group, format="table", complevel=1)
        self.store_dataframe()
        self.set_value(
            ATTR_LAST_UPDATE,
            SEP.join((UPDATE_INSERT_ROW, group, json.dumps(data), str(position))),
        )

    @expose_method(
        {
            "group": "Path to existing group",
            "row": "Row index",
            "column": "Column index",
            "data": "Row dict with attributes",
        }
    )
    def update_value(self, group, row, column, value):
        df = pd.read_hdf(self.filepath, key=group)
        df.loc[row, df.columns[column]] = value
        df.to_hdf(self.filepath, group, format="table", complevel=1)
        self.store_dataframe()
        self.set_value(
            ATTR_LAST_UPDATE,
            SEP.join((UPDATE_VALUE, group, str(row), str(column), str(value))),
        )

    @expose_method({"group": "Path to existing group", "row": "Row index"})
    def remove_row(self, group, row):
        """
        Insert new row into group specified by group path.

        :param group: group path
        :type group: string
        :param row: row index
        :type row: int
        """
        df = pd.read_hdf(self.filepath, key=group)
        df.drop(labels=row, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_hdf(self.filepath, group, format="table", complevel=1)
        self.store_dataframe()
        self.set_value(ATTR_LAST_UPDATE, SEP.join((UPDATE_REMOVE_ROW, group, str(row))))

    def store_dataframe(self):
        with open(self.filepath, "rb") as fp:
            self.set_raw_value(ATTR_CONTENT, fp.read())
