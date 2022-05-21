#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from datahub.exceptions import InvalidParameterException
from datahub.exceptions import ResourceNotFoundException
from datahub.exceptions import ResourceExistException
from datahub.exceptions import DatahubException
from datahub.models import BlobRecord
from datahub.models import CursorType
from datahub import DataHub
import fastredis
import traceback
import datetime
import urllib3
import showlog
import json
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
            showlog.warning(e.error_msg)
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
            self.dh.create_blob_topic(
                project_name=project_name,
                topic_name=topic_name,
                shard_count=shard_count,
                life_cycle=life_cycle,
                comment=comment,
                extend_mode=extend_mode
            )
            res = {
                "code": 0,
                "message": "ok",
                "data": ""
            }
            return res
        except InvalidParameterException as e:
            showlog.warning(e.error_msg)
        except ResourceExistException as e:
            showlog.warning(e.error_msg)
        except Exception as e:
            print(traceback.format_exc())
            sys.exit(-1)

    def blob_records_add(
            self,
            project_name: str = "",
            topic_name: str = "",
            blob_data: str = 'blob_data',  # 可以存入字符串类型的字典
            attribute: dict = None,  # 只能传入单层字典
            shard_id='0',  # 指定shard_id，默认为'0'
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
    """
    创建topic
    """
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

        project_auto_create: bool = False,  # 自动创建project
        topic_auto_create: bool = False,  # 自动创建topic
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    while True:
        add_res = basic.blob_records_add(
            project_name=project_name,
            topic_name=topic_name,
            blob_data=blob_data,
            attribute=attribute,
            shard_id=shard_id
        )
        if add_res['code'] == 0:
            return add_res
        else:
            message = add_res['message']
            if 'project does not exist' in message.error_msg and project_auto_create is True:
                # 自动创建project
                showlog.warning('project does not exist, auto creating...')
                project_create_res = project_create(
                    project_name=project_name,
                    comment='py auto create %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    con_info=con_info
                )
                if project_create_res['code'] == 0:
                    showlog.info('create project success')
                    continue
                else:
                    showlog.warning('create project failed')
                    return project_create_res
            elif 'topic does not exist' in message.error_msg and topic_auto_create is True:
                # 自动创建topic
                showlog.warning('topic does not exist, auto creating...')
                blob_topic_create_res = blob_topic_create(
                    project_name=project_name,
                    topic_name=topic_name,
                    comment='py auto create %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    extend_mode=True,
                    con_info=con_info
                )
                if blob_topic_create_res['code'] == 0:
                    showlog.info('topic project success')
                    continue
                else:
                    showlog.info('topic project failed')
                    return blob_topic_create_res
            else:
                return add_res


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


def lazy_save(
        data: dict,
        save_project_name: str,
        save_topic_name: str,
        save_env_file_name_datahub: str,
        error_to_redis: bool = True,
        save_env_file_name_redis: str = 'local.redis.env',
        save_redis_db: int = 0,
        project_auto_create: bool = True,
        topic_auto_create: bool = True
):
    """
    此模块提供了存储json数据到DataHub的功能
    如果存储错误，将暂存在redis中，由错误处理进程继续处理
    :param data: 需要存储的数据，dict类型，单条存储
    :param save_project_name: 存储的目标project
    :param save_topic_name: 存储的目标topic
    :param save_env_file_name_datahub: datahub环境文件
    :param error_to_redis: 是否存储到redis
    :param save_env_file_name_redis: redis环境文件
    :param save_redis_db: redis缓存数据库
    :param project_auto_create: 自动创建project
    :param topic_auto_create: 自动创建topic
    """
    save_res = {
        "code": 0,
        "msg": "ok",
        "success": True
    }
    try:
        while True:
            add_response = blob_records_add(
                project_name=save_project_name,
                topic_name=save_topic_name,
                blob_data=json.dumps(data),
                env_file_name=save_env_file_name_datahub,
                project_auto_create=project_auto_create,
                topic_auto_create=topic_auto_create
            )  # 以blob方式存储，更加灵活
            add_response_code = add_response.get('code')
            if add_response_code == 0:
                return save_res
            elif add_response_code == 404:
                message = add_response.get('message')
                save_res['code'] = add_response_code
                save_res['msg'] = message
                save_res['success'] = False
                return save_res
            else:
                if error_to_redis is True:
                    fastredis.list_add_r(
                        key=save_topic_name,
                        value=json.dumps(data),
                        env_file_name=save_env_file_name_redis,
                        db=save_redis_db
                    )
                return save_res
    except:
        if error_to_redis is True:
            try:
                # 出错的转存到redis
                fastredis.list_add_r(
                    key=save_topic_name,
                    value=json.dumps(data),
                    env_file_name=save_env_file_name_redis,
                    db=save_redis_db
                )
            except:
                save_res = {
                    "code": 1,
                    "msg": "failed",
                    "success": False
                }
        else:
            save_res = {
                "code": 1,
                "msg": "failed",
                "success": False
            }
        return save_res
