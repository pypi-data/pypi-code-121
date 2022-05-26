from typing import List
from mlplatform_lib.api_client import ApiClient, RunMode
from mlplatform_lib.dataclass import (
    ColumnOfTableFromDefaultSource,
    TableFromDefaultDataSourceInfo,
    DataObject,
    DataObjectOutCol,
    DataObjectInfoList,
)
from mlplatform_lib.hyperdata.hyperdata_http_client import (
    HyperdataHttpClient,
    HYPERDATA_DATETIME_FORMAT,
)
from mlplatform_lib.hyperdata.hyperdata_local_checker import HyperdataLocalChecker
import os
import pathlib
import pandas as pd
from datetime import datetime


class HyperdataApi:
    def __init__(self, api_client: ApiClient = None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        if self.api_client.run_mode == RunMode.LOCAL:
            self.local_checker = HyperdataLocalChecker(api_client=api_client)
            self.local_checker.run()
            self.api_client.projectId = self.local_checker.project_id
            self.api_client.userId = self.api_client.user_id
            self.api_client.Authorization = self.local_checker.access_token
            self.api_client.refreshToken = self.local_checker.refresh_token

        self.hyperdata_client = HyperdataHttpClient(
            hd_addr=self.api_client.hyperdata_addr, api_client=api_client
        )

    def download_csv(self, do_id: int, data_rootpath: str) -> str:
        result, sep, line_delim = self.hyperdata_client.download_do_to_csv(do_id)

        pathlib.Path(data_rootpath).mkdir(parents=True, exist_ok=True)
        csv_path = os.path.join(data_rootpath, "%d.csv" % int(do_id))

        csv_str = result.data.decode("utf-8")
        if line_delim != "\n":
            csv_str.replace(line_delim, "\n")
        with open(csv_path, "w") as f:
            f.write(csv_str)

        if sep != ",":
            data = pd.read_csv(csv_path, sep=sep)
            data.to_csv(csv_path, sep=",", index=False)

        return csv_path


    def create_inference_result(self, table_name: str, object_name: str, columns: List[str]) -> int:
        default_datasource_id = self.hyperdata_client.get_default_datasource_id()
        table_list = self.hyperdata_client.get_dataobject_tables(datasource_id=default_datasource_id)

        if table_name not in [table_info.name for table_info in table_list.db_source_data_object_candidate]:
            self.hyperdata_client.create_dataobject_table(
                datasource_id=default_datasource_id,
                table_from_default_data_source=TableFromDefaultDataSourceInfo(
                    table_name=table_name,
                    column_list=[
                        ColumnOfTableFromDefaultSource(column_name=column, type="VARCHAR")
                        for column in columns
                    ],
                ),
            )
        else:
            print(f"table {table_name} already exists. skip create dataobject table")

        do_info_list = self.hyperdata_client.get_do_list_by_datasource_id(
            datasource_id=self.hyperdata_client.get_default_datasource_id(),
        )

        if object_name not in [object_info.name for object_info in do_info_list.data_object_info_list]:
            do_info_list = self.hyperdata_client.create_dataobjects(
                datasource_id=default_datasource_id,
                dataobjects=DataObjectInfoList(
                    data_object_info_list=[
                        DataObject(
                            id=0,
                            name=object_name,
                            source_table_name=table_name,
                            subtype="Inference Result",
                            out_cols=[DataObjectOutCol(name=column) for column in columns],
                            share_relation=[],
                            author="",
                            description="",
                            created_on=datetime.now().strftime(HYPERDATA_DATETIME_FORMAT),
                            last_edited=datetime.now().strftime(HYPERDATA_DATETIME_FORMAT),
                        )
                    ]
                ),
            )
            print(f"saved do id : {do_info_list.data_object_info_list[0].id}")
            return int(do_info_list.data_object_info_list[0].id)
        else:
            print(f"dataobject {object_name} already exists. skip create dataobject")
            for object_info in do_info_list.data_object_info_list:
                if object_info.name == object_name:
                    print(f"saved do id : {object_info.id}")
                    return int(object_info.id)
