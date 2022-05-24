"""
:Author: ChenXiaolei
:Date: 2020-03-24 10:42:34
:LastEditTime: 2022-05-18 15:41:38
:LastEditors: ChenXiaolei
:Description: StudioBaseHandler
"""

from seven_framework.web_tornado.base_handler.base_cookie_handler import *
from seven_framework.redis import *

from seven_studio.models.db_models.product.product_info_model import *
from seven_studio.models.db_models.user.user_login_model import *
from seven_studio.models.db_models.user.user_info_model import *
from seven_studio.models.db_models.menu.menu_info_model_ex import *
from seven_studio.models.db_models.role.role_user_model import *
from seven_studio.models.db_models.role.role_power_model_ex import *
from seven_studio.models.db_models.log.log_action_model import *
from seven_studio.models.seven_model import PageInfo
from seven_studio.models.enum import *


class StudioBaseHandler(BaseCookieHandler):
    """
    :description: StudioBaseHandler
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    def options_async(self):
        self.reponse_json_success()

    def check_xsrf_cookie(self):
        return

    def add_action_log(self, module_code, content, record_time=None):
        """
        :description: 添加平台操作行为日志
        :param module_code: 模块标识
        :param content: 日志内容
        :param record_time: 日志时间 默认当前时间
        :return 成功 True 失败 False
        :last_editors: ChenXiaolei
        """
        op_result = False
        try:
            if not record_time:
                record_time = TimeHelper.get_now_timestamp()
            user_id = self.request_user_id()
            client_ip = self.get_remote_ip()
            log_action = LogAction()
            log_action.module_code = module_code
            log_action.user_id = user_id
            log_action.content = content
            log_action.record_time = record_time
            log_action.client_ip = client_ip

            if LogActionModel().add_entity(log_action) > 0:
                op_result = True
            return op_result
        except:
            self.logger_error.error(f"添加平台行为日志时异常:{traceback.format_exc()}")
            return False

    def json_dumps(self, rep_dic):
        """
        :description: 用于将字典形式的数据转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJingCan
        """
        if hasattr(rep_dic, '__dict__'):
            rep_dic = rep_dic.__dict__
        return json.dumps(rep_dic, ensure_ascii=False, cls=JsonEncoder)

    def reponse_custom(self, rep_dic):
        """
        :description: 输出公共json模型
        :param rep_dic: 字典类型数据
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        self.http_reponse(self.json_dumps(rep_dic))

    def reponse_common(self, result_code, result_message, data=None):
        """
        :description: 输出公共json模型
        :param result_code: 字符串，服务端返回的错误码
        :param result_message: 字符串，服务端返回的错误信息
        :param data: 返回结果对象，即为数组，字典
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        if hasattr(data, '__dict__'):
            data = data.__dict__
        rep_dic = {}
        rep_dic['ResultCode'] = result_code
        rep_dic['ResultMessage'] = result_message
        rep_dic['Data'] = data

        self.http_reponse(self.json_dumps(rep_dic))

    def reponse_json_success(self, data=None, desc='调用成功'):
        """
        :description: 通用成功返回json结构
        :param data: 返回结果对象，即为数组，字典
        :param desc: 字符串，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        self.reponse_common("0", desc, data)

    def reponse_json_error(self, desc='error'):
        """
        :description: 通用错误返回json结构
        :param desc: 字符串，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        self.reponse_common("1", desc)

    def reponse_json_error_params(self, desc='params error'):
        """
        :description: 参数错误返回json结构
        :param desc: 字符串，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        self.reponse_common("1", desc)

    def redis_init(self, db=None):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJingCan
        """
        redis_cli = RedisHelper.redis_init(config_dict=config.get_value("redis"))
        return redis_cli

    def set_default_headers(self):
        allow_origin_list = config.get_value("allow_origin_list")
        origin = self.request.headers.get("Origin")
        if origin in allow_origin_list:
            self.set_header("Access-Control-Allow-Origin", origin)

        self.set_header("Access-Control-Allow-Headers", "Origin,X-Requested-With,Content-Type,Accept,User-Token,Manage-ProductID,Manage-PageID,PYCKET_ID")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS,PUT,DELETE")
        self.set_header("Access-Control-Allow-Credentials", "true")

    def request_header_token(self):
        header_token = {}
        if "User-Token" in self.request.headers:
            reqInfoList = str.split(self.request.headers["User-Token"], ";")
            for info in reqInfoList:
                kv = str.split(info, "=")
                header_token[kv[0]] = kv[1]
        return header_token

    def request_user_id(self):
        header_token = self.request_header_token()
        if not header_token.__contains__("UserID"):
            return ""
        return header_token["UserID"]

    def request_user_id_md5(self):
        header_token = self.request_header_token()
        if not header_token.__contains__("UserIDMD5"):
            return ""
        return header_token["UserIDMD5"]

    def request_user_token(self):
        header_token = self.request_header_token()
        if not header_token.__contains__("UserToken"):
            return ""
        return header_token["UserToken"]

    def request_product_id(self):
        header_product_id = ""
        if self.request.headers.__contains__("Manage-Productid"):
            header_product_id = self.request.headers["Manage-Productid"]
        product_id = int(header_product_id) if header_product_id.strip() != "" else 0
        if product_id == 0:
            product_id = int(self.get_param("manage-productid", "0"))
        return product_id

    def request_manage_page_id(self):
        if not self.request.headers.__contains__("Manage-PageID"):
            return ""
        return self.request.headers["Manage-PageID"]

    def get_product_info(self):
        product_info = None
        product_id = self.request_product_id()
        if product_id > 0:
            product_info = ProductInfoModel(config.get_value("base_manage_context_key")).get_entity_by_id(product_id)
        return product_info

    def get_curr_user_info(self):
        user_info = None
        user_id = self.request_user_id()
        if user_id:
            user_info = UserInfoModel(self.get_manage_context_key()).get_entity_by_id(user_id)
        return user_info

    def get_base_user_info(self):
        user_info = None
        user_id = self.request_user_id()
        if user_id:
            user_info = UserInfoModel(config.get_value("base_manage_context_key")).get_entity_by_id(user_id)
        return user_info

    def get_is_super(self):
        base_user_info = self.get_base_user_info()
        is_super = False
        if base_user_info:
            is_super = True if base_user_info.IsSuper == 1 else False
        return is_super

    def get_manage_context_key(self):
        manage_context_key = config.get_value("manage_context_key")
        product_info = self.get_product_info()
        if product_info:
            manage_context_key = product_info.ManageContextKey
        return manage_context_key

    def get_file_context_key(self):
        file_context_key = config.get_value("file_context_key")
        product_info = self.get_product_info()
        if product_info:
            file_context_key = product_info.FileContextKey
        return file_context_key

    def get_log_context_key(self):
        log_context_key = config.get_value("log_context_key")
        product_info = self.get_product_info()
        if product_info:
            log_context_key = product_info.LogContextKey
        return log_context_key

    def get_page_index(self):
        page_index = 0
        r_page_index = self.get_param("PageIndex", "")
        if not r_page_index == "":
            dict_page_index = json.loads(r_page_index)
            if dict_page_index and dict_page_index.__contains__("Value"):
                page_index = dict_page_index["Value"]
        return page_index

    def get_page_size(self):
        page_size = 10
        r_page_size = self.get_param("PageSize", "")
        if not r_page_size == "":
            dict_page_size = json.loads(r_page_size)
            if dict_page_size and dict_page_size.__contains__("Value"):
                page_size = dict_page_size["Value"]
        return page_size

    def get_page_cote_id(self):
        page_cote_id = ""
        page_id = self.request_manage_page_id()
        if not page_id == "":
            page_cote_id = page_id.split("$")[1] if page_id.__contains__("$") else ""
        return page_cote_id

    def get_dict_page_info_list(self, page_index, page_size, p_dict, total=0):
        """
        :description: 获取分页信息
        :param page_index：页索引
        :param page_size：页大小
        :param p_dict：字典列表
        :return: 
        :last_editors: HuangJingCan
        """
        page_info = PageInfo()
        page_info.PageIndex = page_index
        page_info.PageSize = page_size
        page_info.RecordCount = total if total > 0 else len(p_dict)
        page_info.Data = p_dict
        page_info = page_info.get_entity_by_page_info(page_info)
        return page_info.__dict__

    def get_dict_by_keys(self, source_dict, keys):
        """
        :description: 根据key搜索字典，返回key相关字典
        :param source_dict
        :param keys
        :return: 值
        :last_editors: HuangJingCan
        """
        if isinstance(source_dict, str):
            source_dict = json.loads(source_dict)
        result = {}
        key_list = list(keys.split(","))
        for i in key_list:
            if i in source_dict:
                result[i] = source_dict[i]
        return result

    def get_condition_by_body(self):
        """
        :description: 获取页面查询条件
        :param {type} 
        :return: condition, order
        :last_editors: HuangJingCan
        """
        condition = ""
        order = ""
        body_dict = self.request_body_to_dict()
        for item in body_dict:
            if not item.__contains__("PageIndex") and not item.__contains__("PageSize"):
                # print(body_dict[item])
                query_method = json.loads(body_dict[item]).get("QueryMethod")
                query_Value = json.loads(body_dict[item]).get("Value")
                query_type = json.loads(body_dict[item]).get("QueryType")
                # query_data_type = json.loads(body_dict[item]).get("QueryDataType")
                if query_type == "Query" and query_Value != "":
                    if condition != "":
                        condition += " AND "
                    if query_method == QueryMethod.Contains.value:
                        condition += f"{item} LIKE '%{query_Value}%'"
                    elif query_method == QueryMethod.StartsWith.value:
                        condition += f"{item} LIKE '{query_Value}%'"
                    elif query_method == QueryMethod.EndsWith.value:
                        condition += f"{item} LIKE '%{query_Value}'"
                    elif query_method == QueryMethod.Equal.value:
                        condition += f"{item}={query_Value}"
                    elif query_method == QueryMethod.GreaterThan.value:
                        condition += f"{item}>{query_Value}"
                    elif query_method == QueryMethod.GreaterThanOrEqual.value:
                        condition += f"{item}>={query_Value}"
                    elif query_method == QueryMethod.LessThan.value:
                        condition += f"{item}<{query_Value}"
                    elif query_method == QueryMethod.LessThanOrEqual.value:
                        condition += f"{item}<={query_Value}"
                    elif query_method == QueryMethod.NotEqual.value:
                        condition += f"{item}<>{query_Value}"
                if query_type == "Sort" and query_Value != "":
                    order = f"{item} {query_Value}"

        return condition, order

    def get_system_user_table(self):
        """
        :description: 获取系统用户
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        user_dict = UserInfoModel(self.get_manage_context_key()).get_dict_list()
        return user_dict

    def logout(self, user_id):
        """
        :description: 用户退出
        :param user_id：用户id
        :return: 
        :last_editors: HuangJingCan
        """
        if user_id.strip() == "":
            return
        if config.get_value("login_type") == "redis":
            self.redis_init().hdel(config.get_value("redis_provider_name_user_login"), user_id)
        else:
            UserLoginModel(config.get_value("manage_context_key")).del_entity("UserID=%s", user_id)

        self.clear_cookie("UserID")
        self.clear_cookie("UserIDMD5")
        self.clear_cookie("UserToken")

    def login_cookie(self, user_login):
        """
        :description: 登录状态设置
        :param user_login: 登录信息
        :return: user_login
        :last_editors: HuangJingCan
        """
        if config.get_value("login_type") == "redis":
            self.redis_init().hset(config.get_value("redis_provider_name_user_login"), user_login.UserID, self.json_dumps(user_login))
        else:
            user_login_base = UserLoginModel(config.get_value("base_manage_context_key"))
            user_login_base.add_update_entity(user_login, "UserIDMD5=%s,ExpireTime=%s,UserToken=%s", [user_login.UserIDMD5, user_login.ExpireTime, user_login.UserToken])

        cookie_domain = config.get_value("cookie_domain")
        if cookie_domain:
            self.set_cookie("UserID", user_login.UserID, domain=cookie_domain)
            self.set_cookie("UserIDMD5", user_login.UserIDMD5, domain=cookie_domain)
            self.set_cookie("UserToken", user_login.UserToken, domain=cookie_domain)
        else:
            self.set_cookie("UserID", user_login.UserID)
            self.set_cookie("UserIDMD5", user_login.UserIDMD5)
            self.set_cookie("UserToken", user_login.UserToken)

    def check_power_menu(self, api_path, cote_id):
        """
        :description: 权限判断
        :param api_path：路径
        :param cote_id：权限码值
        :return: True or False
        :last_editors: HuangJingCan
        """
        manage_context_key = self.get_manage_context_key()
        menu_info_list = MenuInfoModel(manage_context_key).get_list(f"ApiPath LIKE '%{api_path}%'")
        if not menu_info_list:
            return False
        if len([i for i in menu_info_list if i.IsPower == 0]) > 0:
            return True
        role_user_list = RoleUserModel(manage_context_key).get_list("UserID=%s", params=self.request_user_id())
        role_power_list = RolePowerModelEx(manage_context_key).get_role_power_list([i.RoleID for i in role_user_list])
        cote_list = [i for i in role_power_list if i.CoteID == cote_id]
        menu_list = [i.MenuID for i in menu_info_list]
        if len([i for i in cote_list if menu_list.__contains__(i.MenuID)]) > 0:
            return True
        return False

    def auto_mapper(self, s_model, map_dict=None):
        """
        :description: 对象映射（把map_dict值赋值到实体s_model中）
        :param s_model：需要映射的实体对象
        :param map_dict：被映射的实体字典
        :return: 映射后的实体s_model
        """
        if map_dict:
            field_list = s_model.get_field_list()
            for filed in field_list:
                if filed in map_dict:
                    setattr(s_model, filed, map_dict[filed])
        return s_model


def login_filter(is_need_login=True, optional_params=None):
    """
    :description: 登陆过滤装饰器 仅限handler使用
    :param is_need_login：是否需要登陆
    :param optional_params：其他参数
    :return: handler
    """
    def check_login(handler):
        def wrapper(self, **args):
            base_manage_context_key = config.get_value("base_manage_context_key")
            # 获取头部信息
            header_token = self.request_header_token()
            user_id = header_token["UserID"] if header_token.__contains__("UserID") else ""
            user_token = header_token["UserToken"] if header_token.__contains__("UserToken") else ""
            user_id_md5 = header_token["UserIDMD5"] if header_token.__contains__("UserIDMD5") else ""
            if user_id.strip() == "" or user_token.strip() == "" or user_id_md5.strip() == "":
                return self.reponse_common("NoLogin", "未登录")
            if is_need_login and CryptoHelper.md5_encrypt(user_id, config.get_value("login_encrypt_key")) != user_id_md5:
                return self.reponse_common("NoLogin", "未登录")

            # 登陆日志判断，Redis还是MySQL
            if config.get_value("login_type") == "redis":
                redis_user_login = self.redis_init().hget(config.get_value("redis_provider_name_user_login"), user_id)
                user_login = {}
                if redis_user_login:
                    user_login = json.loads(redis_user_login)

                if not user_login or TimeHelper.format_time_to_datetime(user_login["ExpireTime"]) < TimeHelper.get_now_datetime():
                    if not is_need_login:
                        return
                    self.clear_cookie("UserID")
                    self.clear_cookie("UserIDMD5")
                    self.clear_cookie("UserToken")
                    return self.reponse_common("UserExpire", "用户已过期，请重新登录")
                if user_login["UserToken"] != user_token:
                    if not is_need_login:
                        return
                    self.clear_cookie("UserID")
                    self.clear_cookie("UserIDMD5")
                    self.clear_cookie("UserToken")
                    return self.reponse_common("DeviceExpire", "用户在其他终端登录")

                curr_user_info = UserInfoModel(config.get_value("manage_context_key")).get_entity_by_id(user_id)
                if curr_user_info.IsLock == 1:
                    return self.reponse_common("UserLimit", "用户已被锁，请联系管理员")

                user_login["ExpireTime"] = TimeHelper.add_hours_by_format_time(hour=config.get_value("login_expire"))
                self.redis_init().hset(config.get_value("redis_provider_name_user_login"), user_id, self.json_dumps(user_login))
            else:
                user_login_model = UserLoginModel(base_manage_context_key)
                user_login = user_login_model.get_entity_by_id(user_id)

                if not user_login or TimeHelper.format_time_to_datetime(user_login.ExpireTime) < TimeHelper.get_now_datetime():
                    if not is_need_login:
                        return
                    self.clear_cookie("UserID")
                    self.clear_cookie("UserIDMD5")
                    self.clear_cookie("UserToken")
                    return self.reponse_common("UserExpire", "用户已过期，请重新登录")
                if user_login.UserToken != user_token:
                    if not is_need_login:
                        return
                    self.clear_cookie("UserID")
                    self.clear_cookie("UserIDMD5")
                    self.clear_cookie("UserToken")
                    return self.reponse_common("DeviceExpire", "用户在其他终端登录")

                manage_context_key = self.get_manage_context_key()

                curr_user_info = UserInfoModel(manage_context_key).get_entity_by_id(user_id)
                if not curr_user_info:
                    return self.reponse_common("UserNoExist", "用户不存在，请重新登录")
                if curr_user_info.IsLock == 1:
                    return self.reponse_common("UserLimit", "用户已被锁，请联系管理员")

                if base_manage_context_key != manage_context_key:
                    curr_user_info = UserInfoModel(base_manage_context_key).get_entity_by_id(user_id)
                    if not curr_user_info:
                        return self.reponse_common("UserNoExist", "用户不存在，请重新登录")
                    if curr_user_info.IsLock == 1:
                        return self.reponse_common("UserLimit", "用户已被锁，请联系管理员")

                user_login.ExpireTime = TimeHelper.add_hours_by_format_time(hour=config.get_value("login_expire"))
                user_login_model.update_table(f"ExpireTime='{user_login.ExpireTime}'", "UserID=%s", user_login.UserID)

            return handler(self, **args)

        return wrapper

    return check_login


def power_filter(is_check_power=True, optional_params=None):
    """ 
    权限过滤装饰器 仅限handler使用 
    """
    def check_power(handler):
        def wrapper(self, **args):
            user_info = self.get_curr_user_info()
            base_user_info = self.get_base_user_info()
            if user_info and base_user_info:
                if is_check_power and user_info.IsSuper != 1 and base_user_info.IsSuper != 1:
                    api_path = self.request.path
                    if api_path.strip() == "":
                        return self.reponse_common("NoPower", "没有权限")
                    page_id = self.request_manage_page_id()
                    cote_id = page_id.split("$")[1] if page_id.__contains__("$") else ""
                    if not self.check_power_menu(api_path, cote_id):
                        return self.reponse_common("NoPower", "没有权限")

            return handler(self, **args)

        return wrapper

    return check_power