# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-11 09:10:33
@LastEditTime: 2022-05-24 21:03:05
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_module_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *
from seven_framework import *

class FrameBaseModel():
    """
    :description: 框架业务模型 用于被其他业务模型继承，调用模型之间通用的方法
    """
    def __init__(self, context=None):
        self.context = context
        self.acquire_lock_name = ""
        self.identifier = ""
        self.request_queue_name = ""
        self.handler_name = ""
        self.act_id = 0
        self.module_id = 0
        self.user_id = 0
        self.source_object_id = ""

    def score_algorithm_to_score(self, weight):
        """
        :description: 分数算法，获取分数 = 权重 * 分数因子 + 时间极大值  - 当前时间
        :param weight:权重值
        :return: 分数
        :last_editors: HuangJianYi
        """
        score_fator = 1_000_000_000 #分数因子
        max_timestamp = 2_000_000_000 #时间极大值，秒级别
        score = weight * score_fator + max_timestamp - TimeHelper.get_now_timestamp()
        return score

    def score_algorithm_to_weight(self, score):
        """
        :description: 分数算法，获取分数对应的权重值
        :param score:分数
        :return: 权重值
        :last_editors: HuangJianYi
        """
        score_fator = 1_000_000_000
        return int(score/score_fator)

    def lottery_algorithm_chance(self, prize_list, field_name="chance"):
        """
        :description: 抽奖算法（概率）
        :param prize_list:奖品列表
        :param field_name:字段名称
        :return: 中奖的奖品
        :last_editors: HuangJianYi
        """
        init_value = 0.00
        probability_list = []
        for prize in prize_list:
            current_prize = prize
            current_prize["start_probability"] = init_value
            current_prize["end_probability"] = init_value + float(prize[field_name])
            probability_list.append(current_prize)
            init_value = init_value + float(prize[field_name])
        prize_index = random.uniform(0.00, init_value)
        for prize in probability_list:
            if (prize["start_probability"] <= prize_index and prize_index < prize["end_probability"]):
                return prize

    def lottery_algorithm_probability(self, prize_list, field_name="probability"):
        """
        :description: 抽奖算法（权重）
        :param prize_list:奖品列表
        :param field_name:字段名称
        :return: 中奖的奖品
        :last_editors: HuangJianYi
        """
        init_value = 0
        probability_list = []
        for prize in prize_list:
            current_prize = prize
            current_prize["start_probability"] = init_value
            current_prize["end_probability"] = init_value + prize[field_name]
            probability_list.append(current_prize)
            init_value = init_value + prize[field_name]
        prize_index = random.randint(0, init_value - 1)
        for prize in probability_list:
            if (prize["start_probability"] <= prize_index and prize_index < prize["end_probability"]):
                return prize

    def rewards_status(self):
        """
        :description: 给予奖励的子订单状态
        :param 
        :return: 
        :last_editors: HuangJianYi
        """
        status = [
            #等待卖家发货
            "WAIT_SELLER_SEND_GOODS",
            #卖家部分发货
            "SELLER_CONSIGNED_PART",
            #等待买家确认收货
            "WAIT_BUYER_CONFIRM_GOODS",
            #买家已签收（货到付款专用）
            "TRADE_BUYER_SIGNED",
            #交易成功
            "TRADE_FINISHED"
        ]
        return status

    def refund_status(self):
        """
        :description: 给予奖励的子订单退款状态
        :param 
        :return: 
        :last_editors: HuangJianYi
        """
        status = [
            #没有退款
            "NO_REFUND",
            #退款关闭
            "CLOSED",
            #卖家拒绝退款
            "WAIT_SELLER_AGREE"
        ]
        return status

    def get_order_status_name(self, order_status):
        """
        :description: 获取订单状态名称 -1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功
        :param order_status：订单状态
        :return 订单状态名称
        :last_editors: HuangJianYi
        """
        if order_status == -1:
            return "未付款"
        elif order_status == -2:
            return "付款中"
        elif order_status == 0:
            return "未发货"
        elif order_status == 1:
            return "已发货"
        elif order_status == 2:
            return "不予发货"
        elif order_status == 3:
            return "已退款"
        else:
            return "交易成功"

    def get_business_sub_table(self, key, param_dict):
        """
        :description: 获取分表名称
        :param key:字典key
        :param param_dict:参数字典
        :return:
        :last_editors: HuangJianYi
        """
        if not param_dict or not key:
            return None    
        sub_table_config_list = config.get_value("sub_table_config_list",{})
        sub_table_config = sub_table_config_list.get(key,{"sub_count":0,"sub_ways":0}) #sub_count分表数量，sub_ways分表方式（0-默认1-活动id取模2-用户id取模）
        sub_ways = sub_table_config.get("sub_ways", 0)
        if sub_ways == 1:
            object_id = int(param_dict.get("act_id",0))
        if sub_ways == 2:
            object_id = int(param_dict.get("user_id",0))
        else:
            object_id = 0
        
        return SevenHelper.get_sub_table(object_id, sub_table_config.get("sub_count", 0))
        
    def business_process_executing(self,app_id,act_id,module_id,user_id,login_token,handler_name,check_new_user=False,check_user_nick=True,continue_request_expire=5,acquire_lock_name="",request_limit_num=0,request_limit_time=1,source_object_id=""):
        """
        :description: 业务执行前事件,核心业务如抽奖、做任务需要调用当前方法
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param handler_name:接口名称
        :param check_new_user:是否新用户才能参与
        :param check_user_nick:是否校验昵称为空
        :param continue_request_expire:连续请求过期时间，为0不进行校验，单位秒 
        :param acquire_lock_name:分布式锁名称，为空则不开启分布式锁校验功能
        :param request_limit_num:请求限制数(指的是当前接口在指定时间内可以请求的次数，用于流量削峰，减少短时间内的大量请求)；0不限制
        :param request_limit_time:请求限制时间；默认1秒
        :param source_object_id:来源对象标识
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()

        if not act_id or not user_id or not login_token or not handler_name:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data

        #请求太频繁限制
        if continue_request_expire > 0:
            continue_request_key = f"request_business_executing:{handler_name}_{act_id}_{module_id}_{user_id}"
            if source_object_id:
                continue_request_key += f"_{source_object_id}"
            if SevenHelper.is_continue_request(continue_request_key, expire=continue_request_expire * 1000) == True:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = f"对不起,请{continue_request_expire}秒后再试"
                return invoke_result_data
        act_info_model = ActInfoModel(context=self.context)
        act_info_dict = act_info_model.get_cache_dict_by_id(act_id,dependency_key=f"act_info:actid_{act_id}")
        if not act_info_dict or act_info_dict["is_release"] == 0 or act_info_dict["is_del"] == 1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_act"
            invoke_result_data.error_message = "活动信息不存在"
            return invoke_result_data
        now_date = SevenHelper.get_now_datetime()
        act_info_dict["start_date"] = str(act_info_dict["start_date"])
        act_info_dict["end_date"] = str(act_info_dict["end_date"])
        if act_info_dict["start_date"] != "" and act_info_dict["start_date"] != "1900-01-01 00:00:00":
            if now_date < act_info_dict["start_date"]:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "活动将在" + act_info_dict['start_date'] + "开启"
                return invoke_result_data
        if act_info_dict["end_date"] != "" and act_info_dict["end_date"] != "1900-01-01 00:00:00":
            if now_date > act_info_dict["end_date"]:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "活动已结束"
                return invoke_result_data
        act_module_dict = None
        if module_id > 0:
            act_module_model = ActModuleModel(context=self.context)
            act_module_dict = act_module_model.get_cache_dict_by_id(module_id,dependency_key=f"act_module:moduleid_{module_id}")
            if not act_module_dict or act_module_dict["is_release"] == 0 or act_module_dict["is_del"] == 1:
                invoke_result_data.success = False
                invoke_result_data.error_code = "no_module"
                invoke_result_data.error_message = "活动模块信息不存在"
                return invoke_result_data
            act_module_dict["start_date"] = str(act_module_dict["start_date"])
            act_module_dict["end_date"] = str(act_module_dict["end_date"])
            if act_module_dict["start_date"] != "" and act_module_dict["start_date"] != "1900-01-01 00:00:00":
                if now_date < act_module_dict["start_date"]:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "活动将在" + act_module_dict["start_date"] + "开启"
                    return invoke_result_data
            if act_module_dict["end_date"] != "" and act_module_dict["end_date"] != "1900-01-01 00:00:00":
                if now_date > act_module_dict["end_date"]:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "活动已结束"
                    return invoke_result_data

        user_info_model = UserInfoModel(sub_table=self.get_business_sub_table("user_info_tb", {"act_id": act_info_dict["id"], "user_id": 0}),context=self.context)
        id_md5 = CryptoHelper.md5_encrypt_int(f"{act_id}_{user_id}")
        user_info_dict = user_info_model.get_cache_dict("id_md5=%s", limit="1", params=[id_md5], dependency_key=f"user_info:actid_{act_id}_idmd5_{id_md5}")
        if not user_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_user"
            invoke_result_data.error_message = "用户信息不存在"
            return invoke_result_data
        if user_info_dict["app_id"] != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_power"
            invoke_result_data.error_message = "用户信息不存在"
            return invoke_result_data
        if user_info_dict["user_state"] == 1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "user_exception"
            invoke_result_data.error_message = "账号异常,请联系客服处理"
            return invoke_result_data
        if check_new_user == True and user_info_dict["is_new"] == 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "不是新用户"
            return invoke_result_data
        if check_user_nick == True:
            if not user_info_dict["user_nick"] and not user_info_dict["user_nick_encrypt"]:
                invoke_result_data.success = False
                invoke_result_data.error_code = "no_authorize"
                invoke_result_data.error_message = "对不起,请先授权"
                return invoke_result_data
        if user_info_dict["login_token"] != login_token:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "已在另一台设备登录,无法操作"
            return invoke_result_data
        #分布式锁名称存在才进行校验
        identifier = ""
        if acquire_lock_name:
            acquire_lock_status, identifier = SevenHelper.redis_acquire_lock(acquire_lock_name)
            if acquire_lock_status == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "acquire_lock"
                invoke_result_data.error_message = "当前人气火爆,请稍后再试"
                return invoke_result_data
        request_queue_name = ""
        if request_limit_num > 0  and request_limit_time > 0:
            request_queue_name = f"request_queue:{handler_name}_{act_id}_{module_id}"
            if SevenHelper.redis_check_llen(request_queue_name,request_limit_num) == True:
                invoke_result_data.success = False
                invoke_result_data.error_code = "concurrent"
                invoke_result_data.error_message = "当前人气火爆,请稍后再试"
                return invoke_result_data
            SevenHelper.redis_lpush(request_queue_name,user_id,request_limit_time)

        invoke_result_data.data = {}
        invoke_result_data.data["act_info_dict"] = act_info_dict
        invoke_result_data.data["act_module_dict"] = act_module_dict
        invoke_result_data.data["user_info_dict"] = user_info_dict
        invoke_result_data.data["identifier"] = identifier
        invoke_result_data.data["request_queue_name"] = request_queue_name
        
        self.acquire_lock_name = acquire_lock_name
        self.identifier = identifier
        self.request_queue_name = request_queue_name
        self.handler_name = handler_name
        self.act_id = act_id
        self.module_id = module_id
        self.user_id = user_id
        self.source_object_id = source_object_id
        
        return invoke_result_data

    def business_process_executed(self,act_id=0,module_id=0,user_id=0,handler_name="",acquire_lock_name="",identifier="",request_queue_name="",source_object_id=""):
        """
        :description: 业务执行后事件，调用了业务执行前事件需要调用当前方法,参数可以不传，默认用business_process_executing方法传递的参数
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param handler_name:接口名称
        :param acquire_lock_name:分布式锁名称
        :param identifier:分布式锁标识
        :param request_queue_name:请求队列名称
        :param source_object_id:来源对象标识
        :return:
        :last_editors: HuangJianYi
        """
        if not acquire_lock_name:
            acquire_lock_name = self.acquire_lock_name
        if not identifier:
            identifier = self.identifier
        if not request_queue_name:
            request_queue_name = self.request_queue_name
        if not source_object_id:
            source_object_id = self.source_object_id
        if not handler_name:
            handler_name = self.handler_name
        if not act_id:
            act_id = self.act_id
        if not module_id:
            module_id = self.module_id
        if not user_id:
            user_id = self.user_id
             
        continue_request_key = f"request_business_executing:{handler_name}_{act_id}_{module_id}_{user_id}"
        if source_object_id:
            continue_request_key += f"_{source_object_id}"
        SevenHelper.redis_init().delete(continue_request_key)
        if acquire_lock_name and identifier:
            SevenHelper.redis_release_lock(acquire_lock_name,identifier)
        if request_queue_name:
            SevenHelper.redis_lpop(request_queue_name)

    def process_malice_request(self,handler_name,user_id,ip="",user_request_limit_num=30,ip_request_limit_num=30,cycle_type=1,limit_request_time=24):
        """
        :description: 处理恶意请求
        :param handler_name:接口名称
        :param user_id:用户标识
        :param ip:用户ip
        :param user_request_limit_num:用户请求上限数
        :param ip_request_limit_num:ip请求上限数
        :param cycle_type:累计周期类型(1-每分钟 2-每小时 3-每天)
        :param limit_request_time:限制请求时间(单位小时)
        :return:InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if (not user_id and not ip) or not handler_name:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data
        redis_init = SevenHelper.redis_init()
        if user_id:
            objectid_key = f"malice_request:objectid_1_{handler_name}_{user_id}"
            count_key = f"malice_request:count_1_{handler_name}_{user_id}"
            objectid_value = redis_init.get(objectid_key)
            if objectid_value:
                invoke_result_data.success = False
                invoke_result_data.error_code = "malice_request_1"
                invoke_result_data.error_message = "异常操作请稍后再试"
                return invoke_result_data
            count_value = redis_init.get(count_key)
            count_value = int(count_value) if count_value else 0
            if count_value >= user_request_limit_num:
                redis_init.set(objectid_key, 1, limit_request_time * 60 * 60)
            redis_init.incr(count_key, 1)
            if cycle_type == 1:
                redis_init.expire(count_key, 60)
            elif cycle_type == 2:
                redis_init.expire(count_key, 60*60)
            else:
                redis_init.expire(count_key, 24*60*60)
        if ip:
            objectid_key = f"malice_request:objectid_2_{handler_name}_{ip}"
            count_key = f"malice_request:count_2_{handler_name}_{ip}"
            objectid_value = redis_init.get(objectid_key)
            if objectid_value:
                invoke_result_data.success = False
                invoke_result_data.error_code = "malice_request_2"
                invoke_result_data.error_message = "异常操作请稍后再试"
                return invoke_result_data
            count_value = redis_init.get(count_key)
            count_value = int(count_value) if count_value else 0
            if count_value >= ip_request_limit_num:
                redis_init.set(objectid_key, 1, limit_request_time * 60 * 60)
            redis_init.incr(count_key, 1)
            if cycle_type == 1:
                redis_init.expire(count_key, 60)
            elif cycle_type == 2:
                redis_init.expire(count_key, 60*60)
            else:
                redis_init.expire(count_key, 24*60*60)
        return invoke_result_data
        

