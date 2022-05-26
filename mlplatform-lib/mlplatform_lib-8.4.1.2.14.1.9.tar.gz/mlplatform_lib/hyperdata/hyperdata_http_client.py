from mlplatform_lib.dataclass import (
    DataObject,
    TableDescInfo,
    InsertTupleObject,
    TableFromDefaultDataSourceInfo,
    DataObjectInfoList,
    DbSourceDataObjectCandidate,
    DbSourceDataObjectCandidateList,
    FileDownload,
    SelectorProperty,
    ColumnOption,
)
from dataclasses import dataclass
from enum import Enum
import json
import requests
from typing import Optional, Dict, List, Union, Tuple
from mlplatform_lib.utils.dataclass_utils import from_dict, to_dict
from mlplatform_lib.api_client import ApiClient
from mlplatform_lib.auth import Auth
from mlplatform_lib.proauth.proauth_http_client import ProauthHttpClient
import base64


HYPERDATA_DATETIME_FORMAT = "%Y.%m.%d %H.%M.%S"
HYPERDATA_DATETIME_INIT_STR = "1970.01.01 00.00.00"


class HyperdataRequestException(Exception):
    status_code = 200

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class HyperdataRequestType(Enum):
    CREATE = 0
    READ = 1
    UPDATE = 2
    DELETE = 3
    DOWNLOAD = 4
    READ_WITH_FORM_DATA = 5


@dataclass
class HyperdataUserAuth:
    project_id: str
    user_id: str
    authorization: str


@dataclass
class HyperdataRequestResult:
    data: Optional[Union[Dict, List[Dict], bytes]]
    content: Optional[str]
    status_code: Optional[int]


class HyperdataHttpClient:
    def __init__(self, hd_addr, api_client: ApiClient):
        self.base_url = hd_addr + "/hyperdata/web-service"
        self.api_client = api_client
        self.proauth_client = ProauthHttpClient(proauth_addr=api_client.proauth_addr)

    def send_request(
        self,
        service: str,
        rest: Optional[dict],
        query: Optional[dict],
        data: Optional[dict],
        request_type: HyperdataRequestType,
    ) -> HyperdataRequestResult:
        auth = Auth(api_client=self.api_client)
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth.authorization,
            "userId": auth.userId,
        }

        if rest is None:
            rest = {}

        if query is None:
            query = {}

        if data is None:
            data = {}

        if service == "dataObjectTuple":
            headers["doType"] = "inferenceResult"

        if request_type == HyperdataRequestType.DOWNLOAD:
            headers["Content-Type"] = "application/octet-stream"

        url = self.base_url + "/projects/" + str(auth.projectId)
        for key, val in rest.items():
            url = url + "/" + str(key) + "/" + str(val)
        if service != "" and service is not None:
            url = url + "/" + service

        if len(query) != 0:
            url += "?"
            for idx, (key, val) in enumerate(query.items()):
                if idx != 0:
                    url += "&"
                url = url + str(key) + "=" + str(val)

        if data != "" and data is not None:
            data = {"dto": data}
        else:
            data = {"dto": ""}

        if request_type == HyperdataRequestType.READ or request_type == HyperdataRequestType.DOWNLOAD:
            response = requests.get(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == HyperdataRequestType.CREATE:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == HyperdataRequestType.UPDATE:
            response = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == HyperdataRequestType.DELETE:
            response = requests.delete(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == HyperdataRequestType.READ_WITH_FORM_DATA:
            response = requests.get(url, headers=headers, data=json.dumps(data), verify=False)
        else:
            return HyperdataRequestResult(None, None, None)

        if response.status_code == 200:
            if request_type == HyperdataRequestType.DOWNLOAD:
                return HyperdataRequestResult(response.content, None, response.status_code)
            else:
                return HyperdataRequestResult(
                    response.json(), response.content.decode(), response.status_code
                )
        else:
            if response.json()["exception"]["code"] == "HDE-0403":
                result, refresh_token, access_token = self.proauth_client.update_token(auth.refreshToken)
                if result == "true":
                    auth.refreshToken = refresh_token
                    auth.accessToken = access_token
                    auth.authorization = access_token
                    headers["Authorization"] = auth.accessToken

                    if (
                        request_type == HyperdataRequestType.READ
                        or request_type == HyperdataRequestType.DOWNLOAD
                    ):
                        response = requests.get(url, headers=headers, data=json.dumps(data), verify=False)
                    elif request_type == HyperdataRequestType.CREATE:
                        response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
                    elif request_type == HyperdataRequestType.UPDATE:
                        response = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
                    elif request_type == HyperdataRequestType.DELETE:
                        response = requests.delete(url, headers=headers, data=json.dumps(data), verify=False)
                    elif request_type == HyperdataRequestType.READ_WITH_FORM_DATA:
                        response = requests.get(url, headers=headers, data=json.dumps(data), verify=False)
                    else:
                        return HyperdataRequestResult(None, None, None)

                else:
                    raise HyperdataRequestException(response.content.decode(), response.status_code)

            else:
                print(response.content.decode())
                print(
                    (
                        f"cannot connect to {self.base_url}. "
                        f"hyperdata server returns status code {response.status_code}"
                    )
                )
                raise HyperdataRequestException(response.content.decode(), response.status_code)

    # TODO: hyperdata datasource에 do 정보들을 다가지고 오는 so 구현 필요
    def get_do_list(self) -> List[DataObject]:
        result = self.send_request("automlExperimentDataObjectList", {}, {}, {}, HyperdataRequestType.READ)
        result_data = result.data["dto"]["dataObjectInfoList"]

        do_list = []
        for do_info in result_data:
            do_list.append(self.get_do_info(do_info["id"]))
        return do_list

    def get_do_simple_list(self) -> dict:
        result = self.send_request("automlExperimentDataObjectList", {}, {}, {}, HyperdataRequestType.READ)
        result_data = result.data["dto"]["dataObjectInfoList"]
        do_list = {}
        for do_info in result_data:
            do_list[do_info["name"]] = do_info["id"]
        return do_list

    def get_do_list_by_datasource_id(self, datasource_id: int) -> DataObjectInfoList:
        result = self.send_request(
            "dataobjects", {"datasources": datasource_id}, {}, {}, HyperdataRequestType.READ
        )
        result_data = result.data["dto"]["dataObjectInfoList"]
        return DataObjectInfoList(
            data_object_info_list=[from_dict(DataObject, do_info) for do_info in result_data]
        )

    def get_do_info(self, do_id: int) -> DataObject:
        result = self.send_request(
            "", {"dataobjects": do_id}, {"action": "Detail"}, {}, HyperdataRequestType.READ,
        )
        return from_dict(DataObject, result.data["dto"])

    #    def get_do_samples(self, dataobject_id: int, sample_size: int):
    #        return self.send_request(
    #            "",
    #            {"dataobjects": dataobject_id},
    #            {"action": "Sample", "size": sample_size},
    #            {},
    #            auth,
    #            HyperdataRequestType.READ,
    #        )

    # 아직 공식 hyperdata so에서 값이 이상하게 들어와 직접 만든걸 사용
    def get_do_samples(self, dataobject_id: int, sample_size: int) -> HyperdataRequestResult:
        result = self.send_request(
            "automlExperimentDataObjectSample",
            {"dataobjects": dataobject_id},
            {"size": sample_size},
            {},
            HyperdataRequestType.READ,
        )
        fixed_table_string = []
        for row in json.loads(result.data["dto"]["tableString"]):
            fixed_row = {}
            for k, v in row.items():
                fixed_row[k[1:-1]] = v
            fixed_table_string.append(fixed_row)
        result.data["dto"]["tableString"] = json.dumps(fixed_table_string)
        return result

    def get_do_detail_info(self, do_id: int, subtype: str = "Table"):
        result = self.send_request(
            "",
            {"isedit": 0, "subtype": subtype, "dataobjects": do_id},
            {"action": "Desc"},
            {},
            HyperdataRequestType.READ,
        )
        return from_dict(TableDescInfo, result.data["dto"])

    def download_do_to_csv(self, do_id: int) -> Tuple[HyperdataRequestResult, str, str]:
        # 1. get do info
        data_object = self.get_do_info(do_id=do_id)
        # 2. get do detail info
        table_desc_info = self.get_do_detail_info(do_id=do_id, subtype=data_object.subtype)

        # 3. create do to csv in hyperdata
        file_download = FileDownload(
            file_name=data_object.name,
            file_type="csv",
            selector_property=SelectorProperty(
                column_select_options=[
                    ColumnOption(name=col_info.name, alias=col_info.name, type="VARCHAR")
                    for col_info in table_desc_info.col_info_list
                ],
                row_select_options=[],
            ),
            file_token=None,
        )

        result = self.send_request(
            "",
            {"dataobjects": do_id},
            {"action": "FileCreateWithOptions"},
            to_dict(file_download),
            HyperdataRequestType.CREATE,
        )
        file_download = from_dict(FileDownload, result.data["dto"])

        auth = Auth(api_client=self.api_client)
        download_info = (
            f"Authorization::{auth.authorization}"
            f"::userId::{auth.userId}"
            f"::dataObjectId::{data_object.id}"
            f"::filePath::{data_object.name}.csv"
            f"::fileToken::{file_download.file_token}"
        )

        # 4. download csv file
        download_info_encoded_str = base64.b64encode(download_info.encode("utf-8")).decode("utf-8")
        return (
            self.send_request(
                "",
                {"dataobjects": download_info_encoded_str},
                {"action": "FileSecureDownload"},
                {},
                HyperdataRequestType.DOWNLOAD,
            ),
            ",",
            "\\n",
        )

    def get_default_datasource_id(self) -> int:
        result = self.send_request("dataSourceDefault", {}, {}, {}, HyperdataRequestType.READ)
        return int(result.data["dto"]["defaultDataSourceId"])

    def get_dataobject_tables(self, datasource_id: int):
        result = self.send_request(
            "", {"datasources": datasource_id}, {"action": "Desc"}, {}, HyperdataRequestType.READ
        )

        result_data = result.data["dto"]["DbSourceDataObjectCandidate"]
        return DbSourceDataObjectCandidateList(
            db_source_data_object_candidate=[
                from_dict(DbSourceDataObjectCandidate, table_info) for table_info in result_data
            ]
        )

    def create_dataobject_table(
        self, datasource_id: int, table_from_default_data_source: TableFromDefaultDataSourceInfo,
    ) -> None:
        self.send_request(
            "dataobjects",
            {"datasources": datasource_id},
            {"action": "CreateTable"},
            to_dict(table_from_default_data_source),
            HyperdataRequestType.CREATE,
        )

    def create_dataobjects(self, datasource_id: int, dataobjects: DataObjectInfoList) -> DataObjectInfoList:
        result = self.send_request(
            "dataobjects",
            {"datasources": datasource_id},
            {},
            to_dict(dataobjects),
            HyperdataRequestType.CREATE,
        )
        result_data = result.data["dto"]["dataObjectInfoList"]
        return DataObjectInfoList(
            data_object_info_list=[from_dict(DataObject, do_info) for do_info in result_data]
        )

    def insert_dataobject_tuple(
        self, dataobject_id: int, insert_tuple_objects: InsertTupleObject,
    ) -> HyperdataRequestResult:
        return self.send_request(
            "dataObjectTuple",
            {"dataobjects": dataobject_id},
            {},
            {"jsonString": json.dumps(insert_tuple_objects.__dict__)},
            HyperdataRequestType.UPDATE,
        )

    def delete_dataobjects(self, dataobject_id: int) -> HyperdataRequestResult:
        return self.send_request(
            "datasources",
            {},
            {},
            {"dataobjectId": [dataobject_id], "datasourceId": [], "fileType": []},
            HyperdataRequestType.DELETE,
        )
