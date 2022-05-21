#!/usr/bin/env python3
# coding = utf8
from datahub.exceptions import InvalidParameterException
from datahub.exceptions import ResourceExistException
from datahub.exceptions import DatahubException
from datahub.exceptions import ResourceNotFoundException
from datahub.models import BlobRecord
from datahub.models import CursorType
from datahub import DataHub
import traceback
import urllib3
import showlog
import envx
import sys
# datahub安装时使用pydatahub

"""
帮助文档：https://github.com/aliyun/aliyun-datahub-sdk-python
中文文档：https://pydatahub.readthedocs.io/zh_CN/latest/
"""
urllib3.disable_warnings()


def make_con_info(
        env_file_name: str = 'aliyun.datahub.env'
):
    inner_env = envx.read(file_name=env_file_name)
    if inner_env is None or len(inner_env) == 0:
        showlog.warning('[%s]文件不存在或文件填写错误！' % env_file_name)
        exit()
    else:
        access_id = inner_env.get('access_id')
        if access_id is None:
            showlog.warning('access_id不能为空！')
            exit()
        else:
            pass
        access_key = inner_env.get('access_key')
        if access_key is None:
            showlog.warning('access_key不能为空！')
            exit()
        else:
            pass
        endpoint = inner_env.get('endpoint')
        con_info = {
            "access_id": access_id,
            "access_key": access_key,
            "endpoint": endpoint
        }
        return con_info


class Basics:
    def __init__(
            self,
            con_info: dict = None
    ):
        if con_info is None:
            inner_con_info = make_con_info()
        else:
            inner_con_info = con_info

        self.access_id = inner_con_info['access_id']
        self.access_key = inner_con_info['access_key']
        self.endpoint = inner_con_info.get('endpoint')
        self.dh = DataHub(
            access_id=self.access_id,
            access_key=self.access_key,
            endpoint=self.endpoint
        )  # 实例化

    # project操作
    def project_create(
            self,
            project_name: str = None,
            comment: str = 'comment'
    ):
        # create_project接口创建新的Project
        try:
            response = self.dh.create_project(
                project_name=project_name,
                comment=comment
            )
            return response
        except ResourceExistException as e:
            print("project already exist!")
            print("=======================================")
            return

    def project_delete(
            self,
            project_name: str = None
    ):
        # delete_project接口删除Project
        response = self.dh.delete_project(
            project_name=project_name,
        )
        return response

    def project_list(
            self
    ):
        # list_project接口能够获取datahub服务下的所有Project的名字
        response = self.dh.list_project()
        return response.project_names

    def project_get(
            self,
            project_name: str = None
    ):
        # get_project接口获取一个Project的详细信息
        response = self.dh.get_project(
            project_name=project_name
        )
        return response

    # topic操作
        # 类型：TUPLE: 结构化数据, BLOB: 非结构化数据

    def topic_list(
            self,
            project_name: str
    ) -> list:
        """
        获取topic列表
        """
        try:
            response = self.dh.list_topic(
                project_name=project_name,
            )
            topic_names = response.topic_names
            return topic_names
        except ResourceNotFoundException:
            return []

    # Tuple Topic（结构化数据）
    def tuple_topic_create(
            self,
            project_name,
            topic_name,
            shard_count,
            life_cycle,
            record_schema,
            comment='comment'
    ):
        try:
            self.dh.create_tuple_topic(
                project_name=project_name,
                topic_name=topic_name,
                shard_count=shard_count,
                life_cycle=life_cycle,
                record_schema=record_schema,
                comment=comment
            )
            print("create topic success!")
            print("=======================================\n\n")
        except InvalidParameterException as e:
            print(e)
            print("=======================================\n\n")
        except ResourceExistException as e:
            print("topic already exist!")
            print("=======================================\n\n")
        except Exception as e:
            print(traceback.format_exc())
            sys.exit(-1)

    # 新增field
    def tuple_topic_append_field(
            self,
            project_name,
            topic_name,
            field_name,
            field_type
    ):
        self.dh.append_field(
            project_name=project_name,
            topic_name=topic_name,
            field_name=field_name,
            field_type=field_type
        )

    # Blob Topic（非结构化数据）
    def blob_topic_create(
            self,
            project_name,
            topic_name,
            shard_count: int = 1,  # Shard数量
            life_cycle: int = 7,  # 生命周期(1-7)
            comment='comment',  # 描述
            extend_mode=True  # Shard扩展模式：默认是
    ):
        try:
            res = self.dh.create_blob_topic(
                project_name=project_name,
                topic_name=topic_name,
                shard_count=shard_count,
                life_cycle=life_cycle,
                comment=comment,
                extend_mode=extend_mode
            )
            print("create topic success!")
            print("=======================================")
            return res
        except InvalidParameterException as e:
            print(e)
            print("=======================================")
        except ResourceExistException as e:
            print("topic already exist!")
            print("=======================================")
        except Exception as e:
            print(traceback.format_exc())
            sys.exit(-1)

    def blob_records_add(
            self,
            project_name: str = "",
            topic_name: str = "",
            blob_data: str = 'blob_data',  # 可以存入字符串类型的字典
            attribute: dict = None,  # 只能传入单层字典
            shard_id='0'  # 指定shard_id，默认为'0'
    ):
        """
        存入blob数据
        blob_data可以将json转为字符串后存入，json.dumps
        如果存入的字典是单层的，也可以以attribute方式存入
        """

        if len(project_name) == 0:
            showlog.error('project_name error')
            res = {
                "code": -1,
                "message": "project_name error",
                "data": ""
            }
            return res
        if len(topic_name) == 0:
            showlog.error('topic_name error')
            res = {
                "code": -1,
                "message": "topic_name error",
                "data": ""
            }
            return res

        try:
            records_list = list()
            temp_blob_record = BlobRecord(blob_data=blob_data)
            temp_blob_record.shard_id = shard_id
            if attribute is not None:
                for key, value in attribute.items():
                    temp_blob_record.put_attribute(str(key), str(value))
            else:
                pass
            records_list.append(temp_blob_record)
            put_result = self.dh.put_records(
                project_name=project_name,
                topic_name=topic_name,
                record_list=records_list
            )
            failed_record_count = put_result.to_json().get('FailedRecordCount')
            if failed_record_count is not None and failed_record_count == 0:
                res = {
                    "code": 0,
                    "message": "success",
                    "data": put_result.to_json()
                }
                return res
            else:
                # 保存错误log
                showlog.warning(put_result)
                res = {
                    "code": -1,
                    "message": put_result.to_json(),
                    "data": ""
                }
                return res
        except DatahubException as e:
            # 404:NoSuchTopic
            showlog.warning(e)
            res = {
                "code": e.status_code,
                "message": e,
                "data": ""
            }
            return res

    def blob_records_read(
            self,
            project_name: str = "",
            topic_name: str = "",
            next_cursor=None,
            limit_num=10,
            shard_id='0'  # 指定shard_id，默认为'0'
    ):
        """
        读取blob数据
        blob_data可以将json转为字符串后存入，json.dumps
        如果存入的字典是单层的，也可以以attribute方式存入

        返回：
        {
            'NextCursor': '300061a736b40000000000004e260000',
            'RecordCount': 10,
            'StartSeq': 19996,
            'Records': [
                {
                    'Data': 'eyJzZ...I6I',
                    "Sequence": 20004,
                    'SystemTime': 1638348006325
                },
                {

                }
            ]
        }
        其中：SystemTime是数据存到datahub的时间
        """

        if len(project_name) == 0:
            showlog.error('project_name error')
            res = {
                "code": -1,
                "message": "project_name error"
            }
            return res
        if len(topic_name) == 0:
            showlog.error('topic_name error')
            res = {
                "code": -1,
                "message": "topic_name error"
            }
            return res
        while True:
            try:
                if next_cursor is None:
                    tuple_cursor_result = self.dh.get_cursor(
                        project_name=project_name,
                        topic_name=topic_name,
                        shard_id=shard_id,
                        cursor_type=CursorType.OLDEST
                    )
                    cursor = tuple_cursor_result.cursor
                else:
                    cursor = next_cursor
                get_result = self.dh.get_blob_records(
                    project_name=project_name,
                    topic_name=topic_name,
                    shard_id=shard_id,
                    cursor=cursor,
                    limit_num=limit_num
                )
                # print(get_result)
                res = {
                    "code": 0,
                    "message": 'success',
                    "data": get_result.to_json()
                }
                return res
            except DatahubException as e:
                if e.error_code == 'InvalidCursor':
                    showlog.warning('InvalidCursor，将重新获取数据')
                    next_cursor = None
                    continue
                else:
                    showlog.warning(e)
                    res = {
                        "code": -1,
                        "message": e,
                        "data": ""
                    }
                    return res


def project_create(
        project_name: str = None,
        comment: str = 'comment',

        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'aliyun.datahub.env',
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    return basic.project_create(
        project_name=project_name,
        comment=comment
    )


def project_list(
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'aliyun.datahub.env',
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    return basic.project_list()


def blob_topic_create(
        project_name,
        topic_name,
        shard_count: int = 1,  # Shard数量
        life_cycle: int = 7,  # 生命周期(1-7)
        comment='comment',  # 描述
        extend_mode=True,  # Shard扩展模式：默认是

        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'aliyun.datahub.env',
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    return basic.blob_topic_create(
        project_name=project_name,
        topic_name=topic_name,
        shard_count=shard_count,
        life_cycle=life_cycle,
        comment=comment,
        extend_mode=extend_mode
    )


def blob_records_add(
        project_name: str = "",
        topic_name: str = "",
        blob_data: str = 'blob_data',  # 可以存入字符串类型的字典
        attribute: dict = None,  # 只能传入单层字典
        shard_id='0',  # 指定shard_id，默认为'0'

        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'aliyun.datahub.env',
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    return basic.blob_records_add(
        project_name=project_name,
        topic_name=topic_name,
        blob_data=blob_data,
        attribute=attribute,
        shard_id=shard_id
    )


def blob_records_read(
        project_name: str = "",
        topic_name: str = "",
        next_cursor=None,
        limit_num=10,
        shard_id='0',  # 指定shard_id，默认为'0'

        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'aliyun.datahub.env',
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    return basic.blob_records_read(
        project_name=project_name,
        topic_name=topic_name,
        next_cursor=next_cursor,
        limit_num=limit_num,
        shard_id=shard_id
    )


def topic_list(
        project_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'aliyun.datahub.env',
) -> list:
    """
    获取topic列表
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    return basic.topic_list(
        project_name=project_name
    )
