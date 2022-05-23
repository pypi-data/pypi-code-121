# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-19 13:37:16
@LastEditTime: 2022-05-20 11:40:17
@LastEditors: HuangJianYi
@Description: 
"""
import threading, multiprocessing
from seven_framework.console.base_console import *
from seven_cloudapp_frame.models.seven_model import InvokeResultData
from seven_cloudapp_frame.models.frame_base_model import FrameBaseModel
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.console_models.timing_work_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_queue_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_orm_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_report_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_log_model import *


class StatConsoleModel():
    """
    :description: 统计控制台业务模型
    """
    def console_stat_queue(self, mod_count=1):
        """
        :description: 控制台统计上报
        :param mod_count: 单表队列数
        :return: 
        :last_editors: HuangJianYi
        """

        stat_process_ways = config.get_value("stat_process_ways","mysql")
        if stat_process_ways == "mysql":
            for i in range(mod_count):
                t = threading.Thread(target=self._process_stat_queue, args=[i, mod_count])
                t.start()
        else:
            for i in range(10):
                j = threading.Thread(target=self._process_redis_stat_queue, args=[i])
                j.start()

        clea_data_work = ClearDataWork()
        clea_data_work.start_hours = 3
        clea_data_work.end_hours = 4
        clea_data_work.sleep_time = 3600
        clea_data_work.start_work("清理统计流水数据作业")

    def _process_stat_queue(self, mod_value, mod_count):
        """
        :description: 处理mysql统计队列
        :param mod_value: 当前队列值
        :param mod_count: 队列数
        :return: 
        :last_editors: HuangJianYi
        """
        print(f"{TimeHelper.get_now_format_time()} 统计队列{mod_value}启动")
        while True:
            try:
                time.sleep(0.1)
                db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
                stat_queue_model = StatQueueModel(db_transaction=db_transaction)
                del_stat_queue_model = StatQueueModel(sub_table="del", db_transaction=db_transaction)
                stat_orm_model = StatOrmModel()
                now_date = TimeHelper.get_now_format_time()
                if mod_count == 1:
                    stat_queue_list = stat_queue_model.get_list(f"process_count<10 and '{now_date}'>process_date", order_by="process_date asc", limit="100")
                else:
                    stat_queue_list = stat_queue_model.get_list(f"MOD(user_id,{mod_count})={mod_value} and process_count<10 and '{now_date}'>process_date", order_by="process_date asc", limit="100")
                if len(stat_queue_list) > 0:
                    for stat_queue in stat_queue_list:
                        try:
                            frame_base_model = FrameBaseModel(None)
                            stat_log_model = StatLogModel(sub_table=frame_base_model.get_business_sub_table("stat_log_tb", {"act_id": stat_queue.act_id, "user_id": stat_queue.user_id}), db_transaction=db_transaction)
                            stat_report_model = StatReportModel(sub_table=frame_base_model.get_business_sub_table("stat_report_tb", {"act_id": stat_queue.act_id, "user_id": 0}), db_transaction=db_transaction)
                            stat_orm = stat_orm_model.get_cache_entity("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and key_name=%s", params=[stat_queue.act_id, stat_queue.module_id, stat_queue.key_name])
                            if not stat_orm:
                                stat_queue_model.del_entity("id=%s", params=[stat_queue.id])
                                continue
                            create_date = TimeHelper.format_time_to_datetime(stat_queue.create_date)
                            create_day_int = int(create_date.strftime('%Y%m%d'))
                            create_month_int = int(create_date.strftime('%Y%m'))
                            create_year_int = int(create_date.strftime('%Y'))
                            is_add = True
                            if stat_orm.repeat_type > 0:
                                if stat_orm.repeat_type == 2:
                                    stat_log_total = stat_log_model.get_cache_total("act_id=%s and module_id=%s and orm_id=%s and user_id=%s", params=[stat_queue.act_id, stat_queue.module_id, stat_orm.id, stat_queue.user_id])
                                else:
                                    stat_log_total = stat_log_model.get_cache_total("act_id=%s and module_id=%s and orm_id=%s and user_id=%s and create_day=%s", params=[stat_queue.act_id, stat_queue.module_id, stat_orm.id, stat_queue.user_id, create_day_int])
                                if stat_log_total > 0:
                                    is_add = False

                            stat_log = StatLog()
                            stat_log.app_id = stat_queue.app_id
                            stat_log.act_id = stat_queue.act_id
                            stat_log.module_id = stat_queue.module_id
                            stat_log.orm_id = stat_orm.id
                            stat_log.user_id = stat_queue.user_id
                            stat_log.open_id = stat_queue.open_id
                            stat_log.key_value = stat_queue.key_value
                            stat_log.create_day = create_day_int
                            stat_log.create_month = create_month_int
                            stat_log.create_date = create_date

                            stat_report_condition = "act_id=%s and module_id=%s and key_name=%s and create_day=%s"
                            stat_report_param = [stat_queue.act_id, stat_queue.module_id, stat_queue.key_name, create_day_int]
                            stat_report_total = stat_report_model.get_cache_total(stat_report_condition, params=stat_report_param)

                            db_transaction.begin_transaction()
                            if is_add:
                                if stat_report_total == 0:
                                    stat_report = StatReport()
                                    stat_report.app_id = stat_queue.app_id
                                    stat_report.act_id = stat_queue.act_id
                                    stat_report.module_id = stat_queue.module_id
                                    stat_report.key_name = stat_queue.key_name
                                    stat_report.key_value = stat_queue.key_value
                                    stat_report.create_date = create_date
                                    stat_report.create_year = create_year_int
                                    stat_report.create_month = create_month_int
                                    stat_report.create_day = create_day_int
                                    stat_report_model.add_entity(stat_report)
                                else:
                                    stat_report_model.update_table(f"key_value=key_value+{stat_queue.key_value}", stat_report_condition, params=stat_report_param)
                                stat_log_model.add_entity(stat_log)
                            stat_queue_model.del_entity("id=%s", params=[stat_queue.id])
                            del_stat_queue_model.add_entity(stat_queue)
                            result,message = db_transaction.commit_transaction(True)
                            if result == False:
                                raise Exception("执行事务失败", message)
                        except Exception as ex:
                            if db_transaction.is_transaction == True:
                                db_transaction.rollback_transaction()
                            stat_queue.process_count += 1
                            if stat_queue.process_count <= 10:
                                stat_queue.process_result = f"出现异常,json串:{SevenHelper.json_dumps(stat_queue)},ex:{traceback.format_exc()}"
                                minute = 1 if stat_queue.process_count <= 5 else 5
                                stat_queue.process_date = TimeHelper.add_minutes_by_format_time(minute=minute)
                                stat_queue_model.update_entity(stat_queue, "process_count,process_result,process_date")
                            else:
                                logger_error.error(f"统计队列{mod_value}异常,json串:{SevenHelper.json_dumps(stat_queue)},ex:{traceback.format_exc()}")
                            continue
                else:
                    time.sleep(1)
            except Exception as ex:
                logger_error.error(f"统计队列{mod_value}异常,ex:{traceback.format_exc()}")
                time.sleep(5)

    def _process_redis_stat_queue(self, mod_value):
        """
        :description: 处理redis统计队列
        :param mod_value: 当前队列值
        :return: 
        :last_editors: HuangJianYi
        """
        print(f"{TimeHelper.get_now_format_time()} 统计队列{mod_value}启动")

        while True:
            try:
                time.sleep(0.1)
                db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
                stat_orm_model = StatOrmModel()
                redis_init = SevenHelper.redis_init()
                redis_stat_key = f"stat_queue_list:{mod_value}"
                stat_queue_json = redis_init.lindex(redis_stat_key, index=0)
                if not stat_queue_json:
                    time.sleep(1)
                    continue
                try:
                    stat_queue_dict = SevenHelper.json_loads(stat_queue_json)
                    frame_base_model = FrameBaseModel(context=None)
                    stat_log_model = StatLogModel(sub_table=frame_base_model.get_business_sub_table("stat_log_tb", {"act_id": stat_queue_dict["act_id"], "user_id": stat_queue_dict["user_id"]}), db_transaction=db_transaction)
                    stat_report_model = StatReportModel(sub_table=frame_base_model.get_business_sub_table("stat_report_tb", {"act_id": stat_queue_dict["act_id"], "user_id": 0}), db_transaction=db_transaction)
                    stat_orm = stat_orm_model.get_cache_entity("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and key_name=%s", params=[stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_queue_dict["key_name"]])
                    if not stat_orm:
                        continue
                    create_date = TimeHelper.format_time_to_datetime(stat_queue_dict["create_date"])
                    create_day_int = int(create_date.strftime('%Y%m%d'))
                    create_month_int = int(create_date.strftime('%Y%m'))
                    create_year_int = int(create_date.strftime('%Y'))
                    is_add = True
                    if stat_orm.repeat_type > 0:
                        if stat_orm.repeat_type == 2:
                            stat_log_total = stat_log_model.get_cache_total("act_id=%s and module_id=%s and orm_id=%s and user_id=%s", params=[stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_orm.id, stat_queue_dict["user_id"]])
                        else:
                            stat_log_total = stat_log_model.get_cache_total("act_id=%s and module_id=%s and orm_id=%s and user_id=%s and create_day=%s", params=[stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_orm.id, stat_queue_dict["user_id"], create_day_int])
                        if stat_log_total > 0:
                            is_add = False

                    stat_log = StatLog()
                    stat_log.app_id = stat_queue_dict["app_id"]
                    stat_log.act_id = stat_queue_dict["act_id"]
                    stat_log.module_id = stat_queue_dict["module_id"]
                    stat_log.orm_id = stat_orm.id
                    stat_log.user_id = stat_queue_dict["user_id"]
                    stat_log.open_id = stat_queue_dict["open_id"]
                    stat_log.key_value = stat_queue_dict["key_value"]
                    stat_log.create_day = create_day_int
                    stat_log.create_month = create_month_int
                    stat_log.create_date = create_date

                    stat_report_condition = "act_id=%s and module_id=%s and key_name=%s and create_day=%s"
                    stat_report_param = [stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_queue_dict["key_name"], create_day_int]
                    stat_report_total = stat_report_model.get_cache_total(stat_report_condition, params=stat_report_param)

                    if is_add:
                        db_transaction.begin_transaction()
                        if stat_report_total == 0:
                            stat_report = StatReport()
                            stat_report.app_id = stat_queue_dict["app_id"]
                            stat_report.act_id = stat_queue_dict["act_id"]
                            stat_report.module_id = stat_queue_dict["module_id"]
                            stat_report.key_name = stat_queue_dict["key_name"]
                            stat_report.key_value = stat_queue_dict["key_value"]
                            stat_report.create_date = create_date
                            stat_report.create_year = create_year_int
                            stat_report.create_month = create_month_int
                            stat_report.create_day = create_day_int
                            stat_report_model.add_entity(stat_report)
                        else:
                            key_value = stat_queue_dict["key_value"]
                            stat_report_model.update_table(f"key_value=key_value+{key_value}", stat_report_condition, params=stat_report_param)
                        stat_log_model.add_entity(stat_log)
                        result,message = db_transaction.commit_transaction(True)
                        if result == False:
                            raise Exception("执行事务失败", message)
                        else:
                            redis_init.lpop(redis_stat_key)

                except Exception as ex:
                    if db_transaction.is_transaction == True:
                        db_transaction.rollback_transaction()
                    logger_error.error(f"统计队列{mod_value}异常,json串:{SevenHelper.json_dumps(stat_queue_dict)},ex:{traceback.format_exc()}")
                    continue

            except Exception as ex:
                logger_error.error(f"统计队列{mod_value}异常,ex:{traceback.format_exc()}")
                time.sleep(5)

class ClearDataWork(TimingWork):
    """
    :description: 清理数据
    :return: 
    :last_editors: HuangJianYi
    """
    def execute(self):
        invoke_result_data = InvokeResultData()
        sub_table_config_list = config.get_value("sub_table_config_list",{})
        sub_table_config = sub_table_config_list.get("stat_log_tb",{"sub_count":0,"sub_ways":0}) #sub_count分表数量，sub_ways分表方式（0-默认1-活动id取模2-用户id取模）
        sub_count = sub_table_config.get("sub_count", 0)
        if sub_count > 0:
            self.process_sub_table(sub_count)
        else:
            self.process_only_table()

        return invoke_result_data

    def process_only_table(self):
        """
        :description: 处理单表
        :return: 
        :last_editors: HuangJianYi
        """
        stat_log_model = StatLogModel()
        stat_orm_model = StatOrmModel()
        page_index = 0
        while True:
            stat_orm_dict_list, total = stat_orm_model.get_dict_page_list(field="id,repeat_type", page_index=page_index, page_size=50, order_by="id asc")
            if len(stat_orm_dict_list) <= 0:
                break
            for stat_orm_dict in stat_orm_dict_list:
                if stat_orm_dict["repeat_type"] != 2:
                    while True:
                        is_del = stat_log_model.del_entity("orm_id=%s and create_day<%s", params=[stat_orm_dict["id"], SevenHelper.get_now_day_int(-24 * 15)], limit="1000")
                        if is_del == False:
                            break
            page_index += 1

    def process_sub_table(self, sub_count):
        """
        :description: 处理分表
        :param sub_count: 分表数量
        :return: 
        :last_editors: HuangJianYi
        """
        stat_orm_model = StatOrmModel()
        page_index = 0
        while True:
            stat_orm_dict_list, total = stat_orm_model.get_dict_page_list(field="id,repeat_type", page_index=page_index, page_size=50, order_by="id asc")
            if len(stat_orm_dict_list) <= 0:
                break
            for stat_orm_dict in stat_orm_dict_list:
                if stat_orm_dict["repeat_type"] != 2:
                    for i in range(sub_count):
                        stat_log_model = StatLogModel(sub_table=str(i))
                        while True:
                            is_del = stat_log_model.del_entity("orm_id=%s and create_day<%s", params=[stat_orm_dict["id"], SevenHelper.get_now_day_int(-24 * 15)], limit="1000")
                            if is_del == False:
                                break
            page_index += 1
