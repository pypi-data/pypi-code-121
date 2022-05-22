import datetime
import logging
import six
import mongoengine as mg
from . import util
from ... import default
from ...context import flask

logger = logging.getLogger(__name__)


class User(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['keywords']}

    created = mg.DateTimeField(required=True, default=datetime.datetime.now)
    state = mg.StringField(default='normal')
    soft_del = mg.BooleanField(default=False)
    name = mg.StringField()
    info = mg.DictField()
    keywords = mg.ListField()

    def save(self):
        UserAuditLog.record(self, user_id_field_name='id')
        self.keywords = []
        if self.name:
            self.keywords.append(self.name)
        if self.id:
            self.keywords.append(str(self.id))
        for v in self.info.values():
            if v and isinstance(v, six.string_types) and len(v) <= 32 :
                self.keywords.append(v.strip())
        mg.Document.save(self)


class UserAuditLog(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS}

    created = mg.DateTimeField(required=True, default=datetime.datetime.now)
    user_id = mg.StringField(required=True)
    collection_name = mg.StringField()
    editor_id = mg.StringField()
    editor_name = mg.StringField()
    editor_info = mg.DictField()
    fields = mg.ListField()
    delta = mg.ListField()

    @classmethod
    def record(cls, doc, user_id_field_name=None):
        collection_name = doc._collection.name\
                          if doc._collection else str(doc)
        if user_id_field_name:
            user_id = str(getattr(doc, user_id_field_name))
        elif getattr(doc, 'user_id', None):
            user_id = str(doc.user_id)
        else:
            user_id = None
        if not user_id:
            return
        if not getattr(doc, '_changed_fields', None):
            return
        ua_log = UserAuditLog(user_id=user_id,
                              collection_name=collection_name,
                              fields=doc._changed_fields,
                              delta=[])
        for i in doc._delta():
            if not i:
                continue
            for k, v in i.items():
                ua_log.delta.append([k, v])
        try:
            if flask.request and getattr(flask.request, "user", None):
                ua_log.editor_id = str(flask.request.user.id)
                ua_log.editor_name = flask.request.user.name
                ua_log.editor_info = {}
                ua_log.editor_info.update(flask.request.headers)
        except Exception as e:
            logger.exception(e)

        try:
            ua_log.save()
        except Exception as e:
            logger.exception(e)


@util.change_lut_on_save
class PermDesc(mg.Document):
    '''
    权限的描述，用于权限列表的展示，权限的提示等
    '''
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['action', 'name']}
    action = mg.StringField()
    effect = mg.StringField(default="allow")
    resources = mg.ListField()
    name = mg.StringField()
    created = mg.DateTimeField(default=datetime.datetime.now)
    soft_del = mg.BooleanField(default=False)
    lut = mg.DateTimeField(default=datetime.datetime.now)


@util.change_lut_on_save
class RoleDesc(mg.DynamicDocument):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ["foreign_key"]}
    name = mg.StringField()
    perms = mg.ListField()
    granted_positions = mg.ListField()
    foreign_key = mg.StringField()
    info = mg.DictField()
    created = mg.DateTimeField(default=datetime.datetime.now)
    soft_del = mg.BooleanField(default=False)
    lut = mg.DateTimeField(default=datetime.datetime.now)


@util.change_lut_on_save
class PositionDesc(mg.DynamicDocument):
    '''
    职位描述，每个用户通过关联职位描述来确定上下级关系和数据集权限
    --------
    name: string, 职位名称
    parent_id: string, 职位的父级职位id
    path: list, 从根节点到当前节点的id路径，包括根节点，不包括当前节点
    position_type: string, 职位的类型，用于区分一些特殊的职位，比如理财顾问
    '''
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['parent_id',
                        'foreign_key',
                        'tags',
                        'path',
                        'name']}
    name = mg.StringField()
    parent_id = mg.StringField(default='')
    path = mg.ListField()
    position_type = mg.StringField(default='')
    foreign_key = mg.StringField()
    tags = mg.ListField()
    info = mg.DictField()
    created = mg.DateTimeField(default=datetime.datetime.now)
    soft_del = mg.BooleanField(default=False)
    lut = mg.DateTimeField(default=datetime.datetime.now)


@util.change_lut_on_save
class UserPerm(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['user_id',
                        'position_id',
                        'granted_positions']}
    user_id = mg.StringField()
    roles = mg.ListField()
    perms = mg.ListField()
    position_id = mg.StringField()
    granted_positions = mg.ListField()
    created = mg.DateTimeField(default=datetime.datetime.now)
    soft_del = mg.BooleanField(default=False)
    lut = mg.DateTimeField(default=datetime.datetime.now)

    def save(self):
        UserAuditLog.record(self)
        mg.Document.save(self)


class LoginRecord(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['user_id']}

    user_id = mg.StringField(required=True)
    login_type = mg.StringField()
    sid = mg.StringField()
    expiration = mg.DateTimeField()
    info = mg.DictField()
    created = mg.DateTimeField(default=datetime.datetime.now)


@util.change_lut_on_save
class PasswordLogin(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['user_id', 'username']}
    user_id = mg.StringField(required=True)
    username = mg.StringField(required=True)
    password = mg.StringField()
    soft_del = mg.BooleanField(default=False)
    created = mg.DateTimeField(default=datetime.datetime.now)
    lut = mg.DateTimeField(default=datetime.datetime.now)

    def save(self):
        UserAuditLog.record(self)
        Document.save(self)


@util.change_lut_on_save
class ResetPasswordRecord(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['user_id', 'code']}
    user_id = mg.StringField()
    code = mg.StringField()
    query_times = mg.IntField(default=0)
    state = mg.StringField(choices=['created', 'invalid', 'used'],
                           default='created')
    info = mg.DictField()
    timestamp = mg.IntField(default=lambda: int(time.time()))
    created = mg.DateTimeField(default=datetime.datetime.now)
    lut = mg.DateTimeField(default=datetime.datetime.now)


@util.change_lut_on_save
class ThirdPartyLogin(mg.Document):
    meta = {"db_alias": default.MONGOENGINE_ALIAS,
            "indexes": ['user_id', 'ref_id']}
    login_type = mg.StringField()
    user_id = mg.StringField(required=True)
    ref_id = mg.StringField(required=True)
    info = mg.DictField()
    soft_del = mg.BooleanField(default=False)
    created = mg.DateTimeField(default=datetime.datetime.now)
    lut = mg.DateTimeField(default=datetime.datetime.now)
