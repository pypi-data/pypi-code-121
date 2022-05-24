"""
:Author: HuangJingCan
:Date: 2020-03-24 19:48:05
:LastEditTime: 2021-10-14 15:04:44
:LastEditors: HuangJingCan
:Description: 
"""
from seven_studio.handlers.studio_base import *
from seven_studio.libs.geetest import *

from seven_studio.models.db_models.user.user_info_model_ex import *
from seven_studio.models.db_models.role.role_power_model_ex import *
from seven_studio.models.db_models.role.role_user_model import *
from seven_studio.models.db_models.user.user_login_model import *
from seven_studio.models.seven_model import InvokeResult
from seven_studio.libs.file.upload import *


class CoreHandler(StudioBaseHandler):
    def get_async(self):
        result = "后台接口站"
        self.write(result)


class GeetestCodeHandler(StudioBaseHandler):
    """
    :description: 获取极验证的验证码
    """
    def get_async(self):
        user_id = 'test'
        gt = GeetestLib(config.get_value("pc_geetest_id"), config.get_value("pc_geetest_key"))
        status = gt.pre_process(user_id, JSON_FORMAT=0, ip_address="127.0.0.1")
        if not status:
            status = 2
        response_str = gt.get_response_str()

        self.reponse_json_success(response_str)


class LoginPlatformHandler(StudioBaseHandler):
    """
    :description: 登陆
    """
    def get_async(self):
        account = self.get_param("account")
        password = self.get_param("password")
        challenge = self.get_param("challenge")
        validate = self.get_param("validate")
        seccode = self.get_param("seccode")

        if account == "":
            return self.reponse_common("EmptyAccount", "对不起，请你输入账号")

        if password == "":
            return self.reponse_common("EmptyPassword", "对不起，请您输入密码")

        if config.get_value("is_captcha_check"):
            if challenge == "" or validate == "" or seccode == "":
                return self.reponse_common("CaptchaError", "对不起，请先校验验证码")

            result = self.check_code(challenge, validate, seccode)
            if not result:
                return self.reponse_common("CaptchaError", "对不起，验证码验证失败")

        self.reponse_custom(self.login(account, password, True))

    def check_code(self, challenge="", validate="", seccode=""):
        """
        :description: 验证码校验
        :param challenge：challenge
        :param validate：validate
        :param seccode：seccode
        :return: true or false
        :last_editors: HuangJingCan
        """
        gt = GeetestLib(config.get_value("pc_geetest_id"), config.get_value("pc_geetest_key"))
        result = gt.success_validate(challenge, validate, seccode, JSON_FORMAT=0)
        return result == 1

    def login(self, account="", password="", is_platform=False):
        """
        :description: 登录验证
        :param account：账号
        :param password：密码
        :param is_platform：是否平台用户
        :return: invoke_result
        :last_editors: HuangJingCan
        """
        manage_context_key = config.get_value("manage_context_key")
        base_manage_context_key = config.get_value("base_manage_context_key")
        invoke_result = InvokeResult()
        user_info_model = UserInfoModel(base_manage_context_key)
        user_info = user_info_model.get_entity("Account=%s", params=account)
        if not user_info:
            invoke_result.ResultCode = "NoExistAccount"
            invoke_result.ResultMessage = "账号不存在"
            return invoke_result

        if user_info.FaildLoginCount > 4:
            invoke_result.ResultCode = "FaildLoginCountLimit"
            invoke_result.ResultMessage = "密码输入错误限制，请联系管理员解除限制"
            return invoke_result

        verify_password = UserInfoModelEx().verify_password(password, user_info.Password, user_info.UserID)
        if not verify_password:
            user_info.FaildLoginCount += 1
            user_info_model.update_table("FaildLoginCount=%s", "UserID=%s", [user_info.FaildLoginCount, user_info.UserID])
            invoke_result.ResultCode = "ErrorPassword"
            invoke_result.ResultMessage = "密码错误，尝试次数" + str(user_info.FaildLoginCount)
            return invoke_result

        if user_info.IsLock == 1:
            invoke_result.ResultCode = "AccountLock"
            invoke_result.ResultMessage = "对不起你的帐号已经被锁定，请联系管理员解除限制"
            return invoke_result

        is_super = user_info.IsSuper == 1

        if manage_context_key != base_manage_context_key:
            user_info_model_part = UserInfoModel(manage_context_key)
            user_info_curr = user_info_model_part.get_entity("Account=%s", params=account)
            if not user_info_curr:
                invoke_result.ResultCode = "NoExistAccount"
                invoke_result.ResultMessage = "账号不存在"
                return invoke_result
            if user_info_curr.IsLock == 1:
                invoke_result.ResultCode = "AccountLock"
                invoke_result.ResultMessage = "对不起你的帐号已经被锁定，请联系管理员解除限制"
                return invoke_result

            is_super = user_info_curr.IsSuper == 1 or user_info.IsSuper == 1

        # if is_platform and not is_super:
        #     role_user_list = RoleUserModel(manage_context_key).get_list("UserID=%s", params=user_info.UserID)
        #     if len(role_user_list) == 0:
        #         invoke_result.ResultCode = "AccountLock"
        #         invoke_result.ResultMessage = "对不起该账号没有平台管理权限"
        #         return invoke_result

        #     role_power_list = RolePowerModelEx(manage_context_key).get_role_power_list([i.RoleID for i in role_user_list])
        #     if not [i for i in role_power_list if i.MenuID == config.get_value("menu_id_platform")]:
        #         invoke_result.ResultCode = "AccountLock"
        #         invoke_result.ResultMessage = "对不起该账号没有平台管理权限"
        #         return invoke_result

        user_info.FaildLoginCount = 0
        user_info.LoginDate = TimeHelper.get_now_datetime()
        user_info.LoginIP = self.get_remote_ip()
        user_info_model.update_table("FaildLoginCount=%s,LoginDate=%s,LoginIP=%s", "UserID=%s", [user_info.FaildLoginCount, user_info.LoginDate, user_info.LoginIP, user_info.UserID])

        invoke_result.ResultCode = "0"
        invoke_result.ResultMessage = "调用成功"
        invoke_result.Data = self.set_user_info_login_status(user_info).__dict__

        return invoke_result

    def set_user_info_login_status(self, user_info):
        """
        :description: 登录状态设置
        :param user_info：当前登录用户信息
        :return: user_login
        :last_editors: HuangJingCan
        """
        user_login = UserLogin()
        user_login.UserID = user_info.UserID
        user_login.UserIDMD5 = CryptoHelper.md5_encrypt(user_info.UserID, config.get_value("login_encrypt_key"))
        user_login.UserToken = UUIDHelper.get_uuid()
        user_login.ExpireTime = TimeHelper.add_hours_by_format_time(hour=config.get_value("login_expire"))

        self.login_cookie(user_login)

        return user_login


class LogoutHandler(StudioBaseHandler):
    """
    :description: 注销
    """
    def post_async(self):
        """
        :description: 注销用户
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        self.logout(self.request_user_id())

        self.reponse_json_success()


class UploadFilesHandler(StudioBaseHandler):
    """
    :description: 上传图片
    """
    def post_async(self):
        """
        :description: 上传图片
        :param resourceCode：resourceCode
        :param resourceCode：restrictCode
        :return: json
        :last_editors: HuangJingCan
        """
        # 获取参数
        resource_code = self.get_param("resourceCode")
        restrict_code = self.get_param("restrictCode")

        # 验证数据
        if resource_code == "":
            return self.reponse_common("ResourceCodeEmpty", "资源代码不能为空")
        if restrict_code == "":
            return self.reponse_common("RestrictCodeEmpty", "资源限制码不能为空")

        invoke_result = FileUpload(self.get_file_context_key()).upload(resource_code, restrict_code, self.request.files)

        if invoke_result.ResultCode == "0":
            self.reponse_json_success(invoke_result.Data)
        else:
            self.reponse_custom(invoke_result)
