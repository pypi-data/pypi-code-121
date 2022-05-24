
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class UserInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(UserInfoModel, self).__init__(UserInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class UserInfo:

    def __init__(self):
        super(UserInfo, self).__init__()
        self.UserID = ""  # 用户ID
        self.IsSuper = 0  # 是否超管
        self.Account = ""  # 账号
        self.Password = ""  # 密码
        self.Email = ""  # 邮箱
        self.LoginIP = ""  # 登录IP
        self.PasswordQuestion = ""  # 密码问题
        self.PasswordAnswer = ""  # 密码答案
        self.IsLock = 0  # 是否被锁定
        self.CreateDate = "1900-01-01 00:00:00"  # 创建时间
        self.FaildLoginCount = 0  # 登录失败尝试次数
        self.FaildQuestionCount = 0  # 回答问题尝试次数
        self.UserName = ""  # 用户姓名
        self.NickName = ""  # 昵称
        self.JobNo = ""  # 工号
        self.Avatar = ""  # 头像
        self.LoginDate = "1900-01-01 00:00:00"  # 登录时间
        self.Phone = ""  # 手机号码
        self.PersonalitySignature = ""  # 个性签名
        self.UserIDNumber = 0  # 
        self.ChiefUserID = ""  # 直属用户ID

    @classmethod
    def get_field_list(self):
        return ['UserID', 'IsSuper', 'Account', 'Password', 'Email', 'LoginIP', 'PasswordQuestion', 'PasswordAnswer', 'IsLock', 'CreateDate', 'FaildLoginCount', 'FaildQuestionCount', 'UserName', 'NickName', 'JobNo', 'Avatar', 'LoginDate', 'Phone', 'PersonalitySignature', 'UserIDNumber', 'ChiefUserID']
        
    @classmethod
    def get_primary_key(self):
        return "UserID"

    def __str__(self):
        return "cms_userinfo_tb"
    